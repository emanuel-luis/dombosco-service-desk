"""Every write to a request, its staff answer and its comments goes through here.

Each write is atomic, locks the request row with select_for_update() and enforces the
lifecycle rules, so views only parse input, call a service and serialize the result.
`now` is injectable so tests can pin the clock. auto_now and auto_now_add always read the
real clock, so timestamps are written through `_stamp` instead.

Every write also appends its events to the request_events log (`_record`) in the same
transaction, after the domain change, so a rolled-back write leaves no event behind.
"""

import uuid
from collections.abc import Callable
from datetime import datetime
from typing import Any

from django.db import models, transaction
from django.db.models import Q, QuerySet
from django.utils import timezone

from core.models import User
from core.utils import get_role, has_comment_permission, is_dom_bosco_staff, is_parent
from forms.exceptions import RequestConflict, RequestForbidden, RequestInvalid, RequestNotFound
from forms.models import (
    ActorRole,
    Comment,
    EventSource,
    EventType,
    ParentForm,
    RequestEvent,
    StaffForm,
)

Status = ParentForm.StatusChoices
Now = Callable[[], datetime]
Source = EventSource | str

ALLOWED: dict[int, set[int]] = {
    Status.PENDENTE: {Status.ANDAMENTO, Status.CANCELADO},
    Status.ANDAMENTO: {Status.FINALIZADO, Status.CANCELADO},
}
TERMINAL: set[int] = {Status.FINALIZADO, Status.CANCELADO}


def _stamp(obj: models.Model, ts: datetime, **fields: Any) -> None:
    """Save `fields` and updated_at with the injected clock (a plain save() would overwrite it)."""
    type(obj)._default_manager.filter(pk=obj.pk).update(updated_at=ts, **fields)
    for name, value in {"updated_at": ts, **fields}.items():
        setattr(obj, name, value)


def _record(
    event_type: EventType,
    request_id: int,
    user: User,
    ts: datetime,
    *,
    source: EventSource | str = EventSource.API,
    from_status: int | None = None,
    to_status: int | None = None,
    comment_id: int | None = None,
) -> None:
    role = get_role(user)
    RequestEvent.objects.create(
        event_id=uuid.uuid4(),
        request_id=request_id,
        event_type=event_type,
        actor_id=user.pk,
        actor_role=role if role in ActorRole.values else ActorRole.SYSTEM,
        from_status=from_status,
        to_status=to_status,
        comment_id=comment_id,
        occurred_at=ts,
        source=source,
    )


def _is_assigned(user: User, form: ParentForm) -> bool:
    return StaffForm.objects.filter(parent_form=form, assigned_staff=user).exists()


# Reads


def visible_requests(user: User) -> QuerySet[ParentForm]:
    """The one place that decides which requests a user can see."""
    role = get_role(user)
    forms = ParentForm.objects.all()
    if role == "admin":
        return forms
    if role == "staff":
        return forms.filter(Q(status=Status.PENDENTE) | Q(staffform__assigned_staff=user))
    if role == "parent":
        return forms.filter(responsible_party=user)
    raise RequestForbidden()


def get_request(user: User, request_id: int, *, lock: bool = False) -> ParentForm:
    forms = visible_requests(user)
    if lock:
        # of=self: the staff filter joins staffform, whose nullable side cannot be locked.
        forms = forms.select_for_update(of=("self",))
    try:
        return forms.get(pk=request_id)
    except ParentForm.DoesNotExist:
        raise RequestNotFound("Parent form not found.") from None


def list_requests(
    user: User,
    *,
    status: int | None = None,
    assigned_staff: str | None = None,
    responsible_party: str | None = None,
) -> QuerySet[ParentForm]:
    forms = visible_requests(user)
    if status is not None:
        forms = forms.filter(status=status)
    if assigned_staff:
        forms = forms.filter(staffform__assigned_staff__email=assigned_staff)
    if responsible_party:
        forms = forms.filter(responsible_party__email=responsible_party)
    return forms.order_by("status", "created_at")


def list_answers(user: User) -> QuerySet[StaffForm]:
    role = get_role(user)
    answers = StaffForm.objects.all()
    if role == "staff":
        answers = answers.filter(assigned_staff=user)
    elif role == "parent":
        answers = answers.filter(parent_form__responsible_party=user)
    elif role != "admin":
        raise RequestForbidden()
    return answers.order_by("-created_at")


def list_comments(user: User, request_id: int) -> QuerySet[Comment]:
    form = get_request(user, request_id)
    if not has_comment_permission(user, form):
        raise RequestForbidden()
    return Comment.objects.filter(parent_form=form).order_by("created_at")


# Writes: requests


@transaction.atomic
def create_request(
    user: User, data: dict[str, Any], *, now: Now = timezone.now, source: Source = EventSource.API
) -> ParentForm:
    if not is_parent(user, include_superuser=True):
        raise RequestForbidden()
    ts = now()
    form = ParentForm.objects.create(**data, responsible_party=user, status=Status.PENDENTE)
    _stamp(form, ts, created_at=ts)
    _record(EventType.REQUEST_CREATED, form.pk, user, ts, source=source)
    return form


@transaction.atomic
def update_request(
    user: User,
    request_id: int,
    data: dict[str, Any],
    *,
    now: Now = timezone.now,
    source: Source = EventSource.API,
) -> ParentForm:
    form = get_request(user, request_id, lock=True)
    role = get_role(user)
    if role == "parent":
        if form.status != Status.PENDENTE:
            raise RequestConflict("Only pending requests can be changed.")
    elif role != "admin":
        raise RequestForbidden()
    elif form.status in TERMINAL:
        raise RequestConflict("Finished or cancelled requests cannot be changed.")
    ts = now()
    _stamp(form, ts, **data)
    _record(EventType.REQUEST_UPDATED, form.pk, user, ts, source=source)
    return form


@transaction.atomic
def delete_request(
    user: User, request_id: int, *, now: Now = timezone.now, source: Source = EventSource.API
) -> None:
    form = get_request(user, request_id, lock=True)
    role = get_role(user)
    if role == "parent":
        if form.status != Status.PENDENTE:
            raise RequestConflict("Only pending requests can be deleted.")
    elif role != "admin":
        raise RequestForbidden()
    _record(EventType.REQUEST_DELETED, form.pk, user, now(), source=source)
    form.delete()


@transaction.atomic
def change_status(
    user: User,
    request_id: int,
    new_status: int,
    *,
    now: Now = timezone.now,
    source: Source = EventSource.API,
) -> ParentForm:
    if isinstance(new_status, bool) or new_status not in Status.values:
        raise RequestInvalid("Invalid status.")
    role = get_role(user)
    if role not in ("admin", "staff"):
        raise RequestForbidden()
    form = get_request(user, request_id, lock=True)
    if role == "staff":
        if not _is_assigned(user, form):
            raise RequestForbidden()
        if new_status not in ALLOWED.get(form.status, ()):
            raise RequestConflict(
                f"Cannot change the status from {Status(form.status).label} "
                f"to {Status(new_status).label}."
            )
    else:
        # Admins may move in any direction, but the status must stay consistent with the answer:
        # in progress or finished needs a staff answer, pending must not have one.
        answered = StaffForm.objects.filter(parent_form=form).exists()
        if new_status in (Status.ANDAMENTO, Status.FINALIZADO) and not answered:
            raise RequestConflict(
                f"A request without a staff answer cannot be {Status(new_status).label}."
            )
        if new_status == Status.PENDENTE and answered:
            raise RequestConflict("An answered request cannot go back to pending.")
    ts = now()
    old_status = form.status
    _stamp(form, ts, status=new_status)
    _record(
        EventType.STATUS_CHANGED,
        form.pk,
        user,
        ts,
        source=source,
        from_status=old_status,
        to_status=new_status,
    )
    return form


# Writes: staff answer


@transaction.atomic
def answer_request(
    user: User,
    request_id: int,
    data: dict[str, Any],
    *,
    now: Now = timezone.now,
    source: Source = EventSource.API,
) -> StaffForm:
    if not is_dom_bosco_staff(user, include_superuser=True):
        raise RequestForbidden()
    form = get_request(user, request_id, lock=True)
    if StaffForm.objects.filter(parent_form=form).exists():
        raise RequestConflict("This request has already been answered.")
    if form.status != Status.PENDENTE:
        raise RequestConflict(f"Cannot answer a {Status(form.status).label} request.")
    ts = now()
    answer = StaffForm.objects.create(parent_form=form, assigned_staff=user, **data)
    _stamp(answer, ts, created_at=ts)
    _stamp(form, ts, status=Status.ANDAMENTO)
    _record(EventType.STAFF_ANSWERED, form.pk, user, ts, source=source)
    _record(
        EventType.STATUS_CHANGED,
        form.pk,
        user,
        ts,
        source=source,
        from_status=Status.PENDENTE,
        to_status=Status.ANDAMENTO,
    )
    return answer


@transaction.atomic
def update_answer(
    user: User,
    staff_form_id: int,
    data: dict[str, Any],
    *,
    now: Now = timezone.now,
    source: Source = EventSource.API,
) -> StaffForm:
    answer = StaffForm.objects.filter(pk=staff_form_id).first()
    if answer is None:
        visible_requests(user)  # roles with no access get 403 before learning an id is unused
        raise RequestNotFound("Staff form not found.")
    form = get_request(user, answer.parent_form_id, lock=True)
    if answer.assigned_staff_id != user.id and get_role(user) != "admin":
        raise RequestForbidden()
    if form.status in TERMINAL:
        raise RequestConflict("Finished or cancelled requests cannot be changed.")
    ts = now()
    _stamp(answer, ts, **data)
    _record(EventType.STAFF_ANSWER_UPDATED, form.pk, user, ts, source=source)
    return answer


# Writes: comments


@transaction.atomic
def add_comment(
    user: User,
    request_id: int,
    text: str,
    *,
    now: Now = timezone.now,
    source: Source = EventSource.API,
) -> Comment:
    form = get_request(user, request_id, lock=True)
    if not has_comment_permission(user, form):
        raise RequestForbidden()
    if form.status == Status.PENDENTE:
        raise RequestConflict("It is not possible to add comments to a form that is pending.")
    ts = now()
    comment = Comment.objects.create(user=user, parent_form=form, comment=text)
    _stamp(comment, ts, created_at=ts)
    _record(EventType.COMMENT_ADDED, form.pk, user, ts, source=source, comment_id=comment.pk)
    return comment


def _own_comment_in_progress(user: User, comment_id: int) -> Comment:
    comment = Comment.objects.filter(pk=comment_id).first()
    if comment is None:
        visible_requests(user)
        raise RequestNotFound("Comment not found.")
    form = get_request(user, comment.parent_form_id, lock=True)
    if comment.user_id != user.id:
        raise RequestForbidden()
    if form.status != Status.ANDAMENTO:
        raise RequestConflict("Comments can only be changed while the request is in progress.")
    return comment


@transaction.atomic
def edit_comment(
    user: User,
    comment_id: int,
    text: str,
    *,
    now: Now = timezone.now,
    source: Source = EventSource.API,
) -> Comment:
    comment = _own_comment_in_progress(user, comment_id)
    ts = now()
    _stamp(comment, ts, comment=text)
    _record(
        EventType.COMMENT_EDITED,
        comment.parent_form_id,
        user,
        ts,
        source=source,
        comment_id=comment.pk,
    )
    return comment


@transaction.atomic
def delete_comment(
    user: User, comment_id: int, *, now: Now = timezone.now, source: Source = EventSource.API
) -> None:
    comment = _own_comment_in_progress(user, comment_id)
    _record(
        EventType.COMMENT_DELETED,
        comment.parent_form_id,
        user,
        now(),
        source=source,
        comment_id=comment.pk,
    )
    comment.delete()

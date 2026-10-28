"""Derive request_events rows for requests that existed before the log did.

Used by migration 0004 and by `manage.py backfill_request_events`. It takes an apps
registry (the real one or a migration's historical one) and only reads the domain tables
and inserts events, so it is safe to run again: every event id is a uuid5 of what the
event is about, and rows that already exist are skipped.
"""

import uuid
from collections.abc import Iterator
from typing import Any

from django.apps import apps as global_apps
from django.conf import settings

# Fixed forever: changing it would make a rerun insert every event a second time.
NAMESPACE = uuid.UUID("6f1d2c3a-8b4e-4f7a-9c5d-2e1a0b9d7c64")
BATCH_SIZE = 500


def event_id(event_type: str, table: str, pk: int) -> uuid.UUID:
    return uuid.uuid5(NAMESPACE, f"{event_type}:{table}:{pk}")


def _roles(apps: Any) -> dict[int, str]:
    """Role of each user as of now (same precedence as core.utils.get_role)."""
    app_label, model_name = settings.AUTH_USER_MODEL.split(".")
    user_model = apps.get_model(app_label, model_name)
    groups: dict[int, set[str]] = {}
    for user_id, name in user_model.groups.through.objects.values_list("user_id", "group__name"):
        groups.setdefault(user_id, set()).add(name)
    roles = {}
    for pk, superuser, staff in user_model.objects.values_list("pk", "is_superuser", "is_staff"):
        names = groups.get(pk, set())
        if superuser or staff or "Administrador" in names:
            roles[pk] = "admin"
        elif "Colaborador" in names:
            roles[pk] = "staff"
        elif "Responsável" in names:
            roles[pk] = "parent"
    return roles


def _events(apps: Any, roles: dict[int, str]) -> Iterator[dict[str, Any]]:
    # Requests that already have live (api or seed) events keep their real history.
    live = set(
        apps.get_model("forms", "RequestEvent")
        .objects.exclude(source="backfill")
        .values_list("request_id", flat=True)
    )
    parent_form = apps.get_model("forms", "ParentForm")
    staff_form = apps.get_model("forms", "StaffForm")
    comment = apps.get_model("forms", "Comment")

    def event(
        event_type: str, table: str, pk: int, request_id: int, actor_id: int | None, at: Any
    ) -> dict[str, Any]:
        return {
            "event_id": event_id(event_type, table, pk),
            "request_id": request_id,
            "event_type": event_type,
            "actor_id": actor_id,
            "actor_role": roles.get(actor_id, "system") if actor_id else "system",
            "occurred_at": at,
            "source": "backfill",
        }

    answered = set(staff_form.objects.values_list("parent_form_id", flat=True))
    for pk, owner, status, created, updated in (
        parent_form.objects.values_list(
            "pk", "responsible_party_id", "status", "created_at", "updated_at"
        )
        .exclude(pk__in=live)
        .iterator()
    ):
        yield event("request_created", "parent_form", pk, pk, owner, created)
        if status in (2, 3):  # FINALIZADO, CANCELADO
            yield {
                **event("status_changed", "parent_form", pk, pk, None, updated),
                "from_status": 1 if pk in answered else 0,
                "to_status": status,
            }
    for pk, request_id, staff, created in (
        staff_form.objects.values_list("pk", "parent_form_id", "assigned_staff_id", "created_at")
        .exclude(parent_form_id__in=live)
        .iterator()
    ):
        yield event("staff_answered", "staff_form", pk, request_id, staff, created)
        yield {
            **event("status_changed", "staff_form", pk, request_id, staff, created),
            "from_status": 0,
            "to_status": 1,
        }
    for pk, request_id, user, created in (
        comment.objects.values_list("pk", "parent_form_id", "user_id", "created_at")
        .exclude(parent_form_id__in=live)
        .iterator()
    ):
        yield {
            **event("comment_added", "comment", pk, request_id, user, created),
            "comment_id": pk,
        }


def backfill(apps: Any = global_apps) -> int:
    """Insert the missing events and return how many were derived (existing ones included)."""
    model = apps.get_model("forms", "RequestEvent")
    roles = _roles(apps)
    derived = 0
    batch: list[Any] = []
    for fields in _events(apps, roles):
        batch.append(model(**fields))
        derived += 1
        if len(batch) == BATCH_SIZE:
            model.objects.bulk_create(batch, ignore_conflicts=True)
            batch = []
    if batch:
        model.objects.bulk_create(batch, ignore_conflicts=True)
    return derived

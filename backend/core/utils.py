from typing import cast

from django.contrib.auth.models import AnonymousUser
from rest_framework.request import Request

from core.models import User
from forms.models import ParentForm, StaffForm

# request.user is a User or an AnonymousUser; the checks below handle both.
Actor = User | AnonymousUser


def authenticated_user(request: Request) -> User:
    """request.user for views that already require IsAuthenticated, so it is never anonymous."""
    return cast(User, request.user)


def is_superuser(user: Actor) -> bool:
    return user.is_superuser or user.is_staff or user.groups.filter(name="Administrador").exists()


def is_parent(user: Actor, include_superuser: bool = False) -> bool:
    if include_superuser:
        return user.groups.filter(name="Responsável").exists() or user.is_superuser
    return user.groups.filter(name="Responsável").exists()


def is_dom_bosco_staff(user: Actor, include_superuser: bool = False) -> bool:
    if include_superuser:
        return user.groups.filter(name="Colaborador").exists() or user.is_superuser
    return user.groups.filter(name="Colaborador").exists()


ROLES = ("admin", "staff", "parent", "user", "visitor")


def get_role(user: Actor) -> str:
    """Single role for a user, by precedence: admin, staff, parent, user, visitor."""
    if is_superuser(user):
        return "admin"
    if is_dom_bosco_staff(user, include_superuser=True):
        return "staff"
    if is_parent(user):
        return "parent"
    if user.groups.filter(name="Usuário").exists():
        return "user"
    return "visitor"


def has_comment_permission(user: User, parent_form: ParentForm) -> bool:
    """
    Checks if the user is either the responsible party, the assigned staff, or an admin.

    A request that nobody has answered yet has no staff form and no assigned staff.
    """
    return (
        is_superuser(user)
        or parent_form.responsible_party_id == user.id
        or StaffForm.objects.filter(parent_form=parent_form, assigned_staff=user).exists()
    )

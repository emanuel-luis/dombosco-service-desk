from django.contrib.auth.models import User

from forms.models import ParentForm


def is_superuser(user: User) -> bool:
    return user.is_superuser or user.is_staff or user.groups.filter(name="Administrador").exists()


def is_parent(user: User, include_superuser: bool = False) -> bool:
    if include_superuser:
        return user.groups.filter(name="Responsável").exists() or user.is_superuser
    return user.groups.filter(name="Responsável").exists()


def is_dom_bosco_staff(user: User, include_superuser: bool = False) -> bool:
    if include_superuser:
        return user.groups.filter(name="Colaborador").exists() or user.is_superuser
    return user.groups.filter(name="Colaborador").exists()


def has_comment_permission(user: User, parent_form: ParentForm):
    """
    Checks if the user is either the responsible party, the assigned staff, or a superuser.
    """
    return (
        parent_form.responsible_party == user
        or parent_form.staffform.assigned_staff == user
        or is_superuser(user)
    )

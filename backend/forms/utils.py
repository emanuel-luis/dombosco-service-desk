from django.contrib.auth import get_user_model
from django.contrib.auth.models import User


def is_superuser(user: User) -> bool:
    return user.is_superuser or user.is_staff


def is_parent(user: User, include_superuser: bool = False) -> bool:
    if include_superuser:
        return user.groups.filter(name="Pais").exists() or user.is_superuser
    return user.groups.filter(name="Pais").exists() or user.email.endswith("@undb.edu.br")


def is_dom_bosco_staff(user: User, include_superuser: bool = False) -> bool:
    if include_superuser:
        return user.groups.filter(name="Colaborador").exists() or user.is_superuser
    return user.groups.filter(name="Colaborador").exists()

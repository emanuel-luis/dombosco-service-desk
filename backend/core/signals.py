from typing import Any

from allauth.account.models import EmailAddress
from allauth.account.signals import email_confirmed
from django.contrib.auth.models import Group
from django.dispatch import receiver
from django.http import HttpRequest

from core.models import is_staff_email


@receiver(email_confirmed)
def grant_staff_group(
    sender: object, request: HttpRequest, email_address: EmailAddress, **kwargs: Any
) -> None:
    """Staff status needs a verified address at the staff domain, never a typed one."""
    if not is_staff_email(email_address.email):
        return
    user = email_address.user
    colaborador, _ = Group.objects.get_or_create(name="Colaborador")
    user.groups.add(colaborador)
    user.groups.remove(*user.groups.filter(name="Responsável"))

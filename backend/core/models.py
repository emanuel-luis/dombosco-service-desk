from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser, Group
from django.db import models


def is_staff_email(email: str) -> bool:
    """True when the email's domain is DOM_BOSCO_EMAIL_DOMAIN or one of its subdomains.

    Never true when the setting is unset. The setting may carry a leading "@".
    """
    domain = (settings.DOM_BOSCO_EMAIL_DOMAIN or "").strip().lower().lstrip("@")
    if not domain or "@" not in email:
        return False
    email_domain = email.rsplit("@", 1)[1].lower()
    return email_domain == domain or email_domain.endswith("." + domain)


class UserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name="E-mail")
    phone = models.CharField(max_length=20, null=True, blank=True, verbose_name="Telefone")
    mobile_phone = models.CharField(max_length=20, null=True, blank=True, verbose_name="Celular")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

    @property
    def has_staff_email(self):
        """Typed-email check only. It proves nothing about ownership: never use it for access."""
        return is_staff_email(self.email)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Application(models.Model):
    mdm_id = models.CharField(max_length=255, null=False, blank=False, verbose_name="ID MDM")
    name = models.CharField(max_length=255, null=False, blank=False, verbose_name="Nome")
    description = models.TextField(null=True, blank=True, verbose_name="Descrição")

    groups = models.ManyToManyField(Group, verbose_name="Grupos")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Aplicação"
        verbose_name_plural = "Aplicações"

    def __str__(self):
        return self.name

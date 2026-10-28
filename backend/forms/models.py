from typing import Any

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()
BRIEFING_TRUNCATE_LIMIT_CHARACTERS = 50


class ParentForm(models.Model):
    class RelationShipChoices(models.IntegerChoices):
        PAI = 0, "Pai"
        MAE = 1, "Mãe"
        AVO_M = 2, "Avô"
        AVO_F = 3, "Avó"
        TIO = 4, "Tio"
        TIA = 5, "Tia"
        IRMAO = 6, "Irmão"
        IRMA = 7, "Irmã"
        OUTRO = 8, "Outro"

    class StatusChoices(models.IntegerChoices):
        PENDENTE = 0, "Pendente"
        ANDAMENTO = 1, "Em andamento"
        FINALIZADO = 2, "Finalizado"
        CANCELADO = 3, "Cancelado"

    class RequiredByChoices(models.IntegerChoices):
        PAIS = 0, "Solicitado pelos pais"
        ESCOLA = 1, "Solicitado pela Escola"

    @property
    @admin.display(description="Descrição resumida")
    def briefing(self) -> str:
        return (
            self.issue_description[:BRIEFING_TRUNCATE_LIMIT_CHARACTERS] + "..."
            if len(self.issue_description) > BRIEFING_TRUNCATE_LIMIT_CHARACTERS
            else self.issue_description
        )

    @property
    @admin.display(description="Aluno")
    def student(self) -> str:
        return f"{self.student_name} - {self.student_class_name}/{self.student_grade_year}"

    # Seção para Informações do Responsável (entende-se que o usuário já terá isso cadastrado)
    responsible_party = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        verbose_name="Usuário Pai e/ou Responsável",
    )
    requested_by = models.IntegerField(
        choices=RequiredByChoices,
        null=False,
        blank=False,
        verbose_name="Solicitado por",
    )

    # Seção de Informações do Aluno
    student_name = models.CharField(
        max_length=255, null=False, blank=False, verbose_name="Nome do Aluno"
    )
    student_birth_date = models.DateField(
        null=False, blank=False, verbose_name="Data de Nascimento do Aluno"
    )
    student_grade_year = models.PositiveSmallIntegerField(
        null=False, blank=False, verbose_name="Ano do Aluno"
    )
    student_class_name = models.CharField(
        max_length=2, null=False, blank=False, verbose_name="Turma do Aluno"
    )
    relationship_to_student = models.IntegerField(
        choices=RelationShipChoices, null=False, blank=False, verbose_name="Parentesco"
    )

    # Seção para descrição do problema
    issue_description = models.TextField(
        null=False, blank=False, verbose_name="Descrição da solicitação"
    )

    # Metadados de controle do sistema
    status = models.IntegerField(
        default=StatusChoices.PENDENTE,
        choices=StatusChoices,
        null=False,
        blank=False,
        verbose_name="Status",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, editable=False, verbose_name="Data de criação"
    )
    updated_at = models.DateTimeField(
        auto_now=True, editable=False, verbose_name="Data de atualização"
    )


class StaffForm(models.Model):
    assigned_staff = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        verbose_name="Funcionário responsável",
    )

    # Seção de preenchimento da escola
    school_advice = models.TextField(
        null=True, blank=True, verbose_name="Aconselhamento/Observações da escola"
    )
    actions_taken = models.TextField(blank=True, null=True, verbose_name="Providências")
    final_notes = models.TextField(blank=True, null=True, verbose_name="Observações finais")

    # Relacionamento com o formulário de solicitação dos pais, para que possamos rastrear o histórico e obter o protocolo
    parent_form = models.OneToOneField(
        ParentForm,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        verbose_name="Formulário de Solicitação",
    )

    # Metadados de controle do sistema
    created_at = models.DateTimeField(
        auto_now_add=True, editable=False, verbose_name="Data de criação"
    )
    updated_at = models.DateTimeField(
        auto_now=True, editable=False, verbose_name="Data de atualização"
    )


class Comment(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=False, blank=False, verbose_name="Usuário"
    )
    parent_form = models.ForeignKey(
        ParentForm,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        verbose_name="Formulário de Solicitação",
    )
    comment = models.TextField(null=False, blank=False, verbose_name="Comentário")
    created_at = models.DateTimeField(
        auto_now_add=True, editable=False, verbose_name="Data de criação"
    )
    updated_at = models.DateTimeField(
        auto_now=True, editable=False, verbose_name="Data de atualização"
    )


class EventLogImmutable(Exception):
    """request_events is append-only: rows are never updated or deleted."""


class RequestEventQuerySet(models.QuerySet["RequestEvent"]):
    def update(self, **kwargs: Any) -> int:
        raise EventLogImmutable("request_events rows cannot be updated.")

    def delete(self) -> tuple[int, dict[str, int]]:
        raise EventLogImmutable("request_events rows cannot be deleted.")


class EventType(models.TextChoices):
    REQUEST_CREATED = "request_created"
    REQUEST_UPDATED = "request_updated"
    REQUEST_DELETED = "request_deleted"
    STAFF_ANSWERED = "staff_answered"
    STAFF_ANSWER_UPDATED = "staff_answer_updated"
    STATUS_CHANGED = "status_changed"
    COMMENT_ADDED = "comment_added"
    COMMENT_EDITED = "comment_edited"
    COMMENT_DELETED = "comment_deleted"


class EventSource(models.TextChoices):
    API = "api"
    BACKFILL = "backfill"
    SEED = "seed"


class ActorRole(models.TextChoices):
    ADMIN = "admin"
    STAFF = "staff"
    PARENT = "parent"
    SYSTEM = "system"


class RequestEvent(models.Model):
    """Append-only log of what happened to a request.

    No foreign keys (the log outlives deleted requests and users) and no free text or
    student data. Postgres also rejects UPDATE and DELETE with a trigger (migration 0005).
    """

    event_id = models.UUIDField(unique=True)
    request_id = models.BigIntegerField(db_index=True)
    event_type = models.CharField(max_length=32, choices=EventType)
    actor_id = models.BigIntegerField(null=True)
    actor_role = models.CharField(max_length=16, choices=ActorRole)
    from_status = models.SmallIntegerField(null=True)
    to_status = models.SmallIntegerField(null=True)
    comment_id = models.BigIntegerField(null=True)
    occurred_at = models.DateTimeField()
    recorded_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=16, choices=EventSource, default=EventSource.API)

    objects = RequestEventQuerySet.as_manager()

    class Meta:
        db_table = "request_events"
        indexes = [
            models.Index(fields=["request_id", "occurred_at"], name="reqevent_req_time_idx"),
            models.Index(fields=["event_type", "occurred_at"], name="reqevent_type_time_idx"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(event_type__in=[c.value for c in EventType]),
                name="reqevent_event_type_valid",
            )
        ]

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self._state.adding:
            raise EventLogImmutable("request_events rows cannot be updated.")
        super().save(*args, **kwargs)

    def delete(self, *args: Any, **kwargs: Any) -> tuple[int, dict[str, int]]:
        raise EventLogImmutable("request_events rows cannot be deleted.")

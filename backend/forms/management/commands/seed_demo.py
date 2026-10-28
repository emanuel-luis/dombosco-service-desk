import os
import random
from datetime import date, datetime, timedelta
from typing import Any

from allauth.account.models import EmailAddress
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from core.models import User
from forms import services
from forms.models import EventSource, ParentForm

Status = ParentForm.StatusChoices
DOMAIN = "demo.example"
ADMIN_EMAIL = f"admin@{DOMAIN}"
DEFAULT_PASSWORD = "demo-only-change-me"  # public demo credential, never used outside a demo
DAYS = 60
REQUESTS = 60

# Invented names only.
FIRST_NAMES = ["Ana", "Bruno", "Carla", "Diego", "Elisa", "Felipe", "Gabi", "Hugo", "Iris", "Joel"]
LAST_NAMES = ["Alves", "Barros", "Campos", "Duarte", "Esteves", "Faria", "Gomes", "Horta"]
TOPICS = [
    "Dificuldade de adaptação na turma nova",
    "Pedido de reunião sobre as notas do bimestre",
    "Conflito entre colegas no intervalo",
    "Dúvida sobre o plano de estudos de recuperação",
    "Solicitação de apoio pedagógico em matemática",
    "Mudança de turno de transporte escolar",
]

# (email, group, first name)
USERS = [
    (ADMIN_EMAIL, "Administrador", "Admin"),
    (f"staff1@{DOMAIN}", "Colaborador", "Clara"),
    (f"staff2@{DOMAIN}", "Colaborador", "Mateus"),
    (f"parent1@{DOMAIN}", "Responsável", "Paula"),
    (f"parent2@{DOMAIN}", "Responsável", "Renato"),
    (f"parent3@{DOMAIN}", "Responsável", "Sonia"),
    (f"user@{DOMAIN}", "Usuário", "Ulisses"),
    (f"visitor@{DOMAIN}", "Visitante", "Vera"),
]


def _make_user(email: str, group: str, first_name: str, password: str) -> User:
    user = User.objects.create_user(
        email=email,
        password=password,
        first_name=first_name,
        last_name="Demo",
        is_staff=group == "Administrador",
        is_superuser=group == "Administrador",
    )
    user.groups.add(Group.objects.get(name=group))
    EmailAddress.objects.create(user=user, email=email, verified=True, primary=True)
    return user


class Command(BaseCommand):
    help = (
        "Load synthetic demo data (users per group and ~60 requests over the last 60 days). "
        "Needs ALLOW_DEMO_SEED=true. Does nothing when admin@demo.example already exists."
    )

    @transaction.atomic
    def handle(self, *args: Any, **options: Any) -> None:
        if os.environ.get("ALLOW_DEMO_SEED") != "true":
            raise CommandError("Refusing to seed: set ALLOW_DEMO_SEED=true to confirm.")
        if User.objects.filter(email=ADMIN_EMAIL).exists():
            self.stdout.write("Demo data already present, nothing to do.")
            return
        password = os.environ.get("DEMO_PASSWORD") or DEFAULT_PASSWORD
        users = {email: _make_user(email, group, name, password) for email, group, name in USERS}
        admin = users[ADMIN_EMAIL]
        staff = [users[f"staff{i}@{DOMAIN}"] for i in (1, 2)]
        parents = [users[f"parent{i}@{DOMAIN}"] for i in (1, 2, 3)]

        rng = random.Random(42)
        start = timezone.now() - timedelta(days=DAYS)
        offsets = sorted(rng.uniform(0, DAYS - 1) for _ in range(REQUESTS))
        for offset in offsets:
            self._request(rng, start + timedelta(days=offset), admin, staff, parents)
        self.stdout.write(
            f"Seeded {len(USERS)} users and {REQUESTS} requests (password from DEMO_PASSWORD)."
        )

    def _request(
        self,
        rng: random.Random,
        created: datetime,
        admin: User,
        staff: list[User],
        parents: list[User],
    ) -> None:
        clock = created

        def now() -> datetime:
            return clock

        def later(hours: float) -> None:
            nonlocal clock
            clock = min(clock + timedelta(hours=hours), timezone.now())

        kw: dict[str, Any] = {"now": now, "source": EventSource.SEED}
        parent = rng.choice(parents)
        form = services.create_request(
            parent,
            {
                "requested_by": rng.choice([0, 1]),
                "student_name": f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}",
                "student_birth_date": date(2010 + rng.randrange(8), 1 + rng.randrange(12), 15),
                "student_grade_year": rng.randint(1, 9),
                "student_class_name": rng.choice("ABC"),
                "relationship_to_student": rng.randrange(9),
                "issue_description": rng.choice(TOPICS),
            },
            **kw,
        )
        roll = rng.random()
        if roll < 0.15:
            later(rng.uniform(1, 48))
            services.change_status(admin, form.pk, Status.CANCELADO, **kw)
            return
        if roll < 0.25:
            return  # still pending
        worker = rng.choice(staff)
        later(rng.uniform(1, 72))
        services.answer_request(
            worker, form.pk, {"school_advice": "Acompanhamento iniciado pela coordenação."}, **kw
        )
        for _ in range(rng.randint(0, 2)):
            later(rng.uniform(1, 24))
            services.add_comment(rng.choice([parent, worker]), form.pk, "Segue o combinado.", **kw)
        outcome = rng.random()
        if outcome < 0.2:
            return  # in progress
        later(rng.uniform(4, 120))
        final = Status.CANCELADO if outcome < 0.3 else Status.FINALIZADO
        services.change_status(worker, form.pk, final, **kw)
        if final == Status.FINALIZADO and rng.random() < 0.1:
            later(rng.uniform(1, 24))
            services.change_status(admin, form.pk, Status.ANDAMENTO, **kw)
            later(rng.uniform(1, 48))
            services.change_status(admin, form.pk, Status.FINALIZADO, **kw)

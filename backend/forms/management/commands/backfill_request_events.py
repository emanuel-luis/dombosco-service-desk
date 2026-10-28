from typing import Any

from django.core.management.base import BaseCommand

from forms.backfill import backfill
from forms.models import RequestEvent


class Command(BaseCommand):
    help = "Derive request_events rows for existing requests. Safe to run again."

    def handle(self, *args: Any, **options: Any) -> None:
        derived = backfill()
        self.stdout.write(
            f"Derived {derived} events; request_events now has {RequestEvent.objects.count()} rows."
        )

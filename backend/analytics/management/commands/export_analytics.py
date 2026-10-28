from datetime import date
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandError, CommandParser


class Command(BaseCommand):
    help = (
        "Export request_events, request_lifecycle and daily_throughput as Parquet to "
        "<out>/as_of=<date>/, with a _run.json. The snapshot is every event before the end of "
        "the as-of day (UTC). Safe to run again; a contract failure leaves the partition as it was."
    )

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--as-of",
            required=True,
            type=date.fromisoformat,
            metavar="YYYY-MM-DD",
            help="Last UTC day included in the snapshot.",
        )
        parser.add_argument(
            "--out", type=Path, default=Path("exports"), help="Output root (default: exports)."
        )

    def handle(self, *args: Any, **options: Any) -> None:
        try:
            from analytics.export import ContractViolation, export_partition
        except ImportError as error:
            raise CommandError("pyarrow is missing: run `uv sync --extra export`.") from error
        try:
            run = export_partition(options["as_of"], options["out"])
        except ContractViolation as error:
            raise CommandError(f"Data contract failed, nothing written: {error}") from error
        counts = ", ".join(f"{k}={v}" for k, v in run["row_counts"].items())
        self.stdout.write(f"Exported as_of={run['as_of']} (run {run['run_id']}): {counts}.")

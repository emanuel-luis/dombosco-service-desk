import json
import os
import uuid
from datetime import UTC, date, datetime, timedelta
from io import StringIO

import pyarrow.parquet as pq
import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from analytics import contracts, export
from forms.models import RequestEvent

pytestmark = pytest.mark.django_db

AS_OF = date(2030, 1, 1)
T0 = datetime(2030, 1, 1, tzinfo=UTC)
FILES = ("request_events", "request_lifecycle", "daily_throughput")


def log(request_id, kind, hours, role="system", to_status=None):
    return RequestEvent.objects.create(
        event_id=uuid.uuid4(),
        request_id=request_id,
        event_type=kind,
        actor_role=role,
        to_status=to_status,
        occurred_at=T0 + timedelta(hours=hours),
    )


@pytest.fixture
def events():
    """Day 1: r1 created, answered, finished; r2 created. Day 2: r2 cancelled, r3 created."""
    log(1, "request_created", 1, "parent")
    log(1, "staff_answered", 2, "staff")
    log(1, "status_changed", 3, "staff", 2)
    log(2, "request_created", 23.5, "parent")
    log(2, "status_changed", 24, "admin", 3)  # exactly at the cutoff of 2030-01-01
    log(3, "request_created", 30, "parent")


def run(out, as_of="2030-01-01"):
    stdout = StringIO()
    call_command("export_analytics", "--as-of", as_of, "--out", str(out), stdout=stdout)
    return stdout.getvalue()


def read(out, name, as_of="2030-01-01"):
    return pq.read_table(out / f"as_of={as_of}" / f"{name}.parquet")


def test_snapshot_keeps_events_before_the_end_of_the_as_of_day(events, tmp_path):
    run(tmp_path)
    got = read(tmp_path, "request_events")
    assert got.num_rows == 4
    assert max(got["occurred_at"].to_pylist()) < T0 + timedelta(days=1)
    # r3 and the cancellation happened after the cutoff, so they are not in any dataset.
    assert read(tmp_path, "request_lifecycle")["request_id"].to_pylist() == [1, 2]
    assert read(tmp_path, "daily_throughput").to_pylist() == [
        {"day": date(2030, 1, 1), "opened": 2, "answered": 1, "finished": 1, "cancelled": 0}
    ]
    later = run(tmp_path, "2030-01-02")
    assert "request_events=6" in later


def test_datasets_follow_the_contract_and_events_keep_log_order(events, tmp_path):
    run(tmp_path)
    for name in FILES:
        assert read(tmp_path, name).schema.equals(contracts.SCHEMAS[name], check_metadata=False)
    assert read(tmp_path, "request_events")["request_id"].to_pylist() == [1, 1, 1, 2]


def test_run_json(events, tmp_path):
    run(tmp_path)
    meta = json.loads((tmp_path / "as_of=2030-01-01" / "_run.json").read_text(encoding="utf-8"))
    assert uuid.UUID(meta["run_id"]).version == 4
    assert meta["as_of"] == "2030-01-01"
    started, finished = (datetime.fromisoformat(meta[k]) for k in ("started_at", "finished_at"))
    assert started.utcoffset() == timedelta(0)
    assert started <= finished
    assert meta["row_counts"] == {
        "request_events": 4,
        "request_lifecycle": 2,
        "daily_throughput": 1,
    }
    assert len(meta["contracts"]) == 11
    assert all(c["ok"] for c in meta["contracts"])
    assert meta["pyarrow_version"]


def test_rerun_is_idempotent(events, tmp_path):
    run(tmp_path)
    first = {n: read(tmp_path, n) for n in FILES}
    first_run = json.loads((tmp_path / "as_of=2030-01-01" / "_run.json").read_text("utf-8"))
    run(tmp_path)
    assert {n: read(tmp_path, n) for n in FILES} == first
    assert sorted(p.name for p in tmp_path.iterdir()) == ["as_of=2030-01-01"]
    second_run = json.loads((tmp_path / "as_of=2030-01-01" / "_run.json").read_text("utf-8"))
    assert second_run["run_id"] != first_run["run_id"]


def test_empty_log_exports_empty_datasets(tmp_path):
    assert "request_events=0" in run(tmp_path)
    assert read(tmp_path, "request_lifecycle").num_rows == 0


def test_contract_failure_exits_non_zero_and_keeps_the_previous_partition(
    events, tmp_path, monkeypatch
):
    run(tmp_path)
    before = {n: read(tmp_path, n) for n in FILES}
    run_json = (tmp_path / "as_of=2030-01-01" / "_run.json").read_text("utf-8")
    log(9, "request_created", 4, "parent")  # data changed, so a good re-export would differ

    monkeypatch.setattr(
        export, "check_all", lambda *a: [contracts.CheckResult("request_events.schema", False, "x")]
    )
    with pytest.raises(CommandError, match="request_events.schema: x"):
        run(tmp_path)

    assert {n: read(tmp_path, n) for n in FILES} == before
    assert (tmp_path / "as_of=2030-01-01" / "_run.json").read_text("utf-8") == run_json
    assert sorted(p.name for p in tmp_path.iterdir()) == ["as_of=2030-01-01"]


def test_failed_swap_restores_the_previous_partition(events, tmp_path, monkeypatch):
    run(tmp_path)
    run_json = (tmp_path / "as_of=2030-01-01" / "_run.json").read_text("utf-8")
    real_replace = os.replace

    def flaky(src, dst):
        if ".tmp-" in str(src):
            raise OSError("disk full")
        real_replace(src, dst)

    monkeypatch.setattr(os, "replace", flaky)
    with pytest.raises(OSError, match="disk full"):
        run(tmp_path)
    assert (tmp_path / "as_of=2030-01-01" / "_run.json").read_text("utf-8") == run_json
    assert sorted(p.name for p in tmp_path.iterdir()) == ["as_of=2030-01-01"]


def test_help_and_required_as_of(capsys):
    with pytest.raises(SystemExit):
        call_command("export_analytics", "--help")
    out = capsys.readouterr().out
    assert "--as-of" in out and "--out" in out
    with pytest.raises(CommandError, match="--as-of"):
        call_command("export_analytics")

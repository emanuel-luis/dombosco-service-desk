from datetime import UTC, date, datetime, timedelta

import pyarrow as pa

from analytics import contracts as c

CUTOFF = datetime(2030, 1, 2, tzinfo=UTC)
T = datetime(2030, 1, 1, 8, tzinfo=UTC)


def event(n, request_id=1, **extra):
    row = {
        "event_id": f"id-{n}",
        "request_id": request_id,
        "event_type": "request_created",
        "actor_id": None,
        "actor_role": "parent",
        "from_status": None,
        "to_status": None,
        "comment_id": None,
        "occurred_at": T,
        "source": "api",
    }
    return {**row, **extra}


def lifecycle(request_id):
    return {
        "request_id": request_id,
        "opened_at": T,
        "first_response_at": None,
        "closed_at": None,
        "current_status": 0,
        "deleted": False,
        "hours_to_first_response": None,
        "hours_to_close": None,
    }


def table(name, rows):
    return pa.Table.from_pylist(rows, schema=c.SCHEMAS[name])


def failed(results):
    return {r.name for r in results if not r.ok}


def valid():
    events = table("request_events", [event(1), event(2, request_id=2)])
    life = table("request_lifecycle", [lifecycle(1), lifecycle(2)])
    through = table(
        "daily_throughput",
        [
            {
                "day": date(2030, 1, 1),
                **dict.fromkeys(("opened", "answered", "finished", "cancelled"), 1),
            }
        ],
    )
    return events, life, through


def test_valid_tables_pass_every_check():
    events, life, through = valid()
    results = c.check_all(events, life, through, CUTOFF)
    assert len(results) == 11
    assert failed(results) == set()


def test_empty_tables_pass():
    events, life, through = (
        table(n, []) for n in ("request_events", "request_lifecycle", "daily_throughput")
    )
    assert failed(c.check_all(events, life, through, CUTOFF)) == set()


def test_wrong_type_is_detected():
    events, life, through = valid()
    bad = events.set_column(1, "request_id", pa.array([1, 2], type=pa.int32()))
    assert failed(c.check_request_events(bad, CUTOFF)) == {"request_events.schema"}


def test_wrong_column_order_or_name_is_detected():
    events, *_ = valid()
    assert failed(c.check_request_events(events.select(events.column_names[::-1]), CUTOFF)) == {
        "request_events.schema"
    }
    assert failed(
        c.check_request_events(events.rename_columns(["x"] + events.column_names[1:]), CUTOFF)
    ) == {
        "request_events.schema",
        "request_events.unique_event_id",
    }


def test_duplicate_event_id_is_detected():
    events = table("request_events", [event(1), event(1)])
    assert failed(c.check_request_events(events, CUTOFF)) == {"request_events.unique_event_id"}


def test_null_key_is_detected():
    events = table("request_events", [event(1), event(2, request_id=None)])
    assert failed(c.check_request_events(events, CUTOFF)) == {"request_events.non_null_keys"}
    # Nullable columns may be null.
    assert (
        failed(c.check_request_events(table("request_events", [event(1, actor_id=None)]), CUTOFF))
        == set()
    )


def test_event_at_or_after_the_cutoff_is_detected():
    events = table("request_events", [event(1), event(2, occurred_at=CUTOFF)])
    assert failed(c.check_request_events(events, CUTOFF)) == {
        "request_events.occurred_before_cutoff"
    }
    just_before = table(
        "request_events", [event(1, occurred_at=CUTOFF - timedelta(microseconds=1))]
    )
    assert failed(c.check_request_events(just_before, CUTOFF)) == set()


def test_lifecycle_duplicate_request_and_count_mismatch_are_detected():
    events, *_ = valid()
    duplicated = table("request_lifecycle", [lifecycle(1), lifecycle(1)])
    assert failed(c.check_request_lifecycle(duplicated, events)) == {
        "request_lifecycle.unique_request_id"
    }
    short = table("request_lifecycle", [lifecycle(1)])
    assert failed(c.check_request_lifecycle(short, events)) == {
        "request_lifecycle.row_count_matches_events"
    }


def test_throughput_duplicate_day_is_detected():
    row = {"day": date(2030, 1, 1), "opened": 1, "answered": 0, "finished": 0, "cancelled": 0}
    assert failed(c.check_daily_throughput(table("daily_throughput", [row, row]))) == {
        "daily_throughput.unique_day"
    }

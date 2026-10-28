"""The analytics endpoints: admin only, and 501 where the views cannot exist."""

import pytest
from django.db import connection

from tests.test_analytics_views import scenario  # noqa: F401  (fixture shared with the view tests)

pytestmark = pytest.mark.django_db

ROLES = ["admin", "staff", "parent", "user", "visitor", "anonymous"]
PATHS = ["requests/", "throughput/", "backlog/", "sla/"]
BASE = "/api/v1/analytics/"
ADMIN_STATUS = 200 if connection.vendor == "postgresql" else 501
EXPECTED = {"admin": ADMIN_STATUS, "staff": 403, "parent": 403, "user": 403, "visitor": 403}


@pytest.mark.parametrize("role", ROLES)
@pytest.mark.parametrize("path", PATHS)
def test_permission_matrix(world, api, path, role):
    user = None if role == "anonymous" else getattr(world, role)
    response = api(user).get(BASE + path)
    assert response.status_code == EXPECTED.get(role, 401), response.content


@pytest.mark.skipif(connection.vendor == "postgresql", reason="501 is the non-Postgres answer")
def test_not_postgres_says_so(world, api):
    response = api(world.admin).get(BASE + "sla/")
    assert response.status_code == 501
    assert "PostgreSQL" in response.json()["detail"]


@pytest.mark.parametrize(
    "query",
    ["from=2030-13-01", "to=yesterday", "from=2030-01-02&to=2030-01-01", "from=01/02/2030"],
)
def test_throughput_rejects_bad_dates_before_anything_else(world, api, query):
    response = api(world.admin).get(f"{BASE}throughput/?{query}")
    assert response.status_code == 400, response.content


@pytest.mark.postgres
def test_requests_are_paginated(api, world, scenario):  # noqa: F811
    client = api(world.admin)
    page = client.get(BASE + "requests/?limit=2&offset=1").json()
    assert page["count"] == 5
    assert [r["request_id"] for r in page["results"]] == sorted(scenario.values())[1:3]
    row = client.get(BASE + "requests/").json()["results"][0]
    assert row["hours_to_first_response"] == 2.0  # r1: a number, not a string


@pytest.mark.postgres
@pytest.mark.parametrize(
    ("query", "days"),
    [
        ("", ["2030-01-01", "2030-01-02"]),
        ("from=2030-01-02", ["2030-01-02"]),
        ("to=2030-01-01", ["2030-01-01"]),
        ("from=2030-01-02&to=2030-01-02", ["2030-01-02"]),
        ("from=2030-01-03", []),
    ],
)
def test_throughput_date_filters(api, world, scenario, query, days):  # noqa: F811
    response = api(world.admin).get(f"{BASE}throughput/?{query}")
    assert response.status_code == 200
    assert [row["day"] for row in response.json()] == days


@pytest.mark.postgres
def test_backlog_and_sla_endpoints(api, world, scenario):  # noqa: F811
    client = api(world.admin)
    backlog = {r["current_status"]: r["requests"] for r in client.get(BASE + "backlog/").json()}
    assert backlog == {1: 2, 2: 1, 3: 1}
    sla = client.get(BASE + "sla/").json()
    assert (sla["responded_count"], sla["first_response_p90_hours"]) == (3, 2.8)
    assert (sla["closed_count"], sla["close_p50_hours"]) == (2, 17.0)

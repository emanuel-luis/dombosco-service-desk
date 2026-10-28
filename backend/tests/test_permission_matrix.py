"""Every endpoint and method against the five groups and an anonymous caller.

The caller with the Responsável group owns the requests, the Colaborador is assigned to the
answered one. Bodies are minimal but valid, so a 2xx or 4xx other than 403 means the caller
got past authorization.
"""

import pytest

from forms import services
from forms.models import ParentForm, StaffForm
from tests.conftest import REQUEST_DATA

pytestmark = pytest.mark.django_db

ROLES = ["admin", "staff", "parent", "user", "visitor", "anonymous"]
FORMS = "/api/v1/forms"
CORE = "/api/v1/core"


def expect(*statuses):
    return dict(zip(ROLES, statuses, strict=True))


# method, path ({placeholders} are filled from the scenario), body, status per role
CASES = [
    ("get", f"{FORMS}/parent/", None, expect(200, 200, 200, 403, 403, 401)),
    ("get", f"{FORMS}/parent/?id={{pending}}", None, expect(200, 200, 200, 403, 403, 401)),
    ("post", f"{FORMS}/parent/", REQUEST_DATA, expect(403, 403, 201, 403, 403, 401)),
    (
        "put",
        f"{FORMS}/parent/?id={{pending}}",
        REQUEST_DATA,
        expect(200, 403, 200, 403, 403, 401),
    ),
    ("delete", f"{FORMS}/parent/?id={{pending}}", None, expect(200, 403, 200, 403, 403, 401)),
    ("get", f"{FORMS}/parent/choices/", None, expect(200, 200, 200, 200, 200, 401)),
    (
        "put",
        f"{FORMS}/parent/update-status/?id={{pending}}",
        {"status": 3},
        expect(200, 403, 403, 403, 403, 401),
    ),
    ("get", f"{FORMS}/staff/", None, expect(200, 200, 200, 403, 403, 401)),
    (
        "post",
        f"{FORMS}/staff/",
        {"parent_form_id": "{pending}"},
        expect(403, 201, 403, 403, 403, 401),
    ),
    (
        "put",
        f"{FORMS}/staff/?id={{answer}}",
        {"school_advice": "x"},
        expect(200, 200, 403, 403, 403, 401),
    ),
    ("get", f"{FORMS}/comment/?id={{answered}}", None, expect(200, 200, 200, 403, 403, 401)),
    (
        "post",
        f"{FORMS}/comment/",
        {"parent_form_id": "{answered}", "comment": "x"},
        expect(201, 201, 201, 403, 403, 401),
    ),
    (
        "put",
        f"{FORMS}/comment/?id={{comment}}",
        {"comment": "y"},
        expect(403, 403, 200, 403, 403, 401),
    ),
    ("delete", f"{FORMS}/comment/?id={{comment}}", None, expect(403, 403, 200, 403, 403, 401)),
    ("get", f"{CORE}/groups/", None, expect(200, 403, 403, 403, 403, 401)),
    # GroupSerializer marks name read-only, so an admin POST creates a nameless group (201).
    ("post", f"{CORE}/groups/", {}, expect(201, 403, 403, 403, 403, 401)),
    ("put", f"{CORE}/groups/", {}, expect(404, 403, 403, 403, 403, 401)),
    ("get", f"{CORE}/applications/", None, expect(200, 200, 200, 200, 200, 401)),
    ("post", f"{CORE}/applications/", {}, expect(400, 403, 403, 403, 403, 401)),
    ("put", f"{CORE}/applications/", {}, expect(404, 403, 403, 403, 403, 401)),
    ("get", "/api/v1/auth/user/", None, expect(200, 200, 200, 200, 200, 401)),
]


@pytest.fixture
def scenario(world, make_request):
    pending = make_request(world.parent)
    answered = make_request(world.parent, ParentForm.StatusChoices.ANDAMENTO, world.staff)
    comment = services.add_comment(world.parent, answered.pk, "oi")
    return {
        "pending": pending.pk,
        "answered": answered.pk,
        "answer": StaffForm.objects.get(parent_form=answered).pk,
        "comment": comment.pk,
    }


@pytest.mark.parametrize("role", ROLES)
@pytest.mark.parametrize(
    ("method", "path", "body", "expected"),
    CASES,
    ids=[f"{method.upper()} {path.split('?')[0]}" for method, path, _, _ in CASES],
)
def test_permission_matrix(world, api, scenario, method, path, body, expected, role):
    user = None if role == "anonymous" else getattr(world, role)
    if body is not None:
        body = {
            k: scenario.get(v.strip("{}"), v) if isinstance(v, str) else v for k, v in body.items()
        }
    kwargs = {"format": "json"} if body is not None else {}
    response = getattr(api(user), method)(
        path.format(**scenario), *([body] if body is not None else []), **kwargs
    )
    assert response.status_code == expected[role], response.content

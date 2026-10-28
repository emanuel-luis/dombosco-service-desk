import pytest
from django.contrib.auth import get_user_model

from core.utils import has_comment_permission
from forms.models import ParentForm

pytestmark = pytest.mark.django_db


def make_form(owner):
    return ParentForm.objects.create(
        responsible_party=owner,
        requested_by=0,
        student_name="Aluno",
        student_birth_date="2015-01-01",
        student_grade_year=3,
        student_class_name="A",
        relationship_to_student=0,
        issue_description="Preciso de ajuda",
    )


def test_comment_permission_without_staff_answer_does_not_crash():
    users = get_user_model().objects
    owner = users.create_user(email="owner@example.com", username="owner", password="pw-123456")
    other = users.create_user(email="other@example.com", username="other", password="pw-123456")
    form = make_form(owner)
    assert has_comment_permission(owner, form)
    assert not has_comment_permission(other, form)

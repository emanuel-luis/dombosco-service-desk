"""Thin views: parse input, call forms.services, serialize the result.

Visibility, permissions and lifecycle rules live in forms.services; domain errors are
APIExceptions and become 403, 404, 409 or 400 responses on their own.
"""

from typing import Any

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, serializers, status, views
from rest_framework.request import Request
from rest_framework.response import Response

from core.permissions import IsDomBoscoAdmin, IsDomBoscoParent, IsDomBoscoStaff
from core.utils import authenticated_user
from forms import services
from forms.exceptions import RequestInvalid
from forms.models import ParentForm
from forms.serializers import (
    CommentCreateSerializer,
    CommentSerializer,
    CommentUpdateSerializer,
    IdQuerySerializer,
    ParentQuerySerializer,
    ParentsFormSerializer,
    StaffFormCreateSerializer,
    StaffFormSerializer,
    StaffFormUpdateSerializer,
    StatusChangeResponseSerializer,
    StatusChangeSerializer,
)


def _id_param(request: Request) -> int:
    query = IdQuerySerializer(data=request.query_params)
    if not query.is_valid():
        raise RequestInvalid("You must provide a valid id parameter.")
    id_: int = query.validated_data["id"]
    return id_


def _valid(serializer_class: type[serializers.BaseSerializer[Any]], data: Any) -> dict[str, Any]:
    # data is the raw request body or query: validating it is this function's job.
    serializer = serializer_class(data=data)
    serializer.is_valid(raise_exception=True)
    validated: dict[str, Any] = serializer.validated_data
    return validated


# ParentForm API
class ParentFormViewAPI(views.APIView):
    """
    Allows a parent to submit a form with their information and their child's information.

    The form is saved with the parent's email, so that the staff can contact them.
    A staff cannot submit a form on behalf of a parent, unless they are a parent themselves.
    """

    permission_classes = [
        permissions.IsAuthenticated & (IsDomBoscoStaff | IsDomBoscoParent | IsDomBoscoAdmin)
    ]

    @extend_schema(
        parameters=[ParentQuerySerializer],
        responses={200: ParentsFormSerializer(many=True)},
        description=(
            "Lists the requests the user can see: a parent sees their own, staff see pending "
            "requests plus the ones assigned to them, admins see all. With `id`, returns that "
            "single request instead of a list (404 when the user cannot see it)."
        ),
    )
    def get(self, request: Request) -> Response:
        # Empty query values count as absent, as they always did.
        params = {key: value for key, value in request.query_params.items() if value}
        query = _valid(ParentQuerySerializer, params)
        if "id" in query:
            return Response(
                ParentsFormSerializer(
                    services.get_request(authenticated_user(request), query["id"])
                ).data
            )
        forms = services.list_requests(
            authenticated_user(request),
            status=query.get("status"),
            assigned_staff=query.get("assigned_staff"),
            responsible_party=query.get("responsible_party"),
        )
        return Response(ParentsFormSerializer(forms, many=True).data)

    @extend_schema(request=ParentsFormSerializer, responses={201: ParentsFormSerializer})
    def post(self, request: Request) -> Response:
        """Creates a PENDENTE request owned by the current user (parents only)."""
        data = _valid(ParentsFormSerializer, request.data)
        form = services.create_request(authenticated_user(request), data)
        return Response(ParentsFormSerializer(form).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        parameters=[IdQuerySerializer],
        request=ParentsFormSerializer,
        responses=ParentsFormSerializer,
    )
    def put(self, request: Request) -> Response:
        """Updates a request. A parent can only change their own request while it is PENDENTE."""
        data = _valid(ParentsFormSerializer, request.data)
        form = services.update_request(authenticated_user(request), _id_param(request), data)
        return Response(ParentsFormSerializer(form).data)

    @extend_schema(parameters=[IdQuerySerializer], responses={200: None})
    def delete(self, request: Request) -> Response:
        """Deletes a request. A parent can only delete their own request while it is PENDENTE."""
        services.delete_request(authenticated_user(request), _id_param(request))
        return Response(status=status.HTTP_200_OK)


class ParentFormsChoicesViewAPI(views.APIView):
    """
    Returns the choices for the parent form fields as a dictionary
    to be handled by the frontend.
    """

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses={200: OpenApiTypes.OBJECT})
    def get(self, request: Request) -> Response:
        """Maps each choice field (relationship, status, required_by) to {value: label}."""
        return Response(
            {
                "relationship": dict(ParentForm.RelationShipChoices.choices),
                "status": dict(ParentForm.StatusChoices.choices),
                "required_by": dict(ParentForm.RequiredByChoices.choices),
            },
            status=status.HTTP_200_OK,
        )


class UpdateStatusParentFormAPI(views.APIView):
    """
    Allows a staff member to update the status of a parent form.
    """

    permission_classes = [permissions.IsAuthenticated & (IsDomBoscoStaff | IsDomBoscoAdmin)]

    @extend_schema(
        parameters=[IdQuerySerializer],
        request=StatusChangeSerializer,
        responses=StatusChangeResponseSerializer,
    )
    def put(self, request: Request) -> Response:
        """
        Changes the status of a request.

        Staff can only change requests assigned to them, along 0 -> 1/3 and 1 -> 2/3.
        Admins can set any status, including going backwards. The status can be
        0 PENDENTE, 1 EM ANDAMENTO, 2 FINALIZADO or 3 CANCELADO. A disallowed
        transition is a 409.
        """
        new_status = _valid(StatusChangeSerializer, request.data)["status"]
        form = services.change_status(authenticated_user(request), _id_param(request), new_status)
        return Response(
            data={
                "id": form.id,
                "status": form.status,
                "detail": "Status updated sucessfully.",
            },
            status=status.HTTP_200_OK,
        )


# StaffForm API
class StaffFormViewAPI(views.APIView):
    """
    Allows a staff member to answer a form submitted by a parent.

    The form is saved with the staff member's email, so that the parent can contact them.
    Once a staff member submits a form, the status of the parent form is updated to EM_ANDAMENTO.
    """

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses={200: StaffFormSerializer(many=True)})
    def get(self, request: Request) -> Response:
        """
        Lists staff answers: staff see their own, parents see the answers to their requests,
        admins see all.
        """
        return Response(
            StaffFormSerializer(services.list_answers(authenticated_user(request)), many=True).data
        )

    @extend_schema(request=StaffFormCreateSerializer, responses={201: StaffFormSerializer})
    def post(self, request: Request) -> Response:
        """
        Answers a pending request: assigns the staff member and moves it to EM ANDAMENTO.

        Answering a request twice, or a finished or cancelled one, is a 409.
        """
        data = _valid(StaffFormCreateSerializer, request.data)
        answer = services.answer_request(
            authenticated_user(request), data.pop("parent_form_id"), data
        )
        return Response(StaffFormSerializer(answer).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        parameters=[IdQuerySerializer],
        request=StaffFormUpdateSerializer,
        responses=StaffFormSerializer,
    )
    def put(self, request: Request) -> Response:
        """Updates a staff answer. Only its staff member or an admin, until the request closes."""
        data = _valid(StaffFormUpdateSerializer, request.data)
        answer = services.update_answer(authenticated_user(request), _id_param(request), data)
        return Response(StaffFormSerializer(answer).data)


class CommentViewAPI(views.APIView):
    """
    Comments on a request, for its parent, its assigned staff and admins.

    Only the author can edit or delete a comment, and only while the request is in progress.
    """

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=CommentCreateSerializer, responses={201: CommentSerializer})
    def post(self, request: Request) -> Response:
        """Adds a comment. Rejected with 409 while the request is still PENDENTE."""
        data = _valid(CommentCreateSerializer, request.data)
        comment = services.add_comment(
            authenticated_user(request), data["parent_form_id"], data["comment"]
        )
        return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        parameters=[IdQuerySerializer],
        responses={200: CommentSerializer(many=True)},
        description="Lists the comments of the request given by `id`, oldest first.",
    )
    def get(self, request: Request) -> Response:
        comments = services.list_comments(authenticated_user(request), _id_param(request))
        return Response(CommentSerializer(comments, many=True).data)

    @extend_schema(parameters=[IdQuerySerializer], responses={200: None})
    def delete(self, request: Request) -> Response:
        """Deletes a comment (`id` is the comment id). Author only, while EM ANDAMENTO."""
        services.delete_comment(authenticated_user(request), _id_param(request))
        return Response(status=status.HTTP_200_OK)

    @extend_schema(
        parameters=[IdQuerySerializer],
        request=CommentUpdateSerializer,
        responses=CommentSerializer,
    )
    def put(self, request: Request) -> Response:
        """Edits a comment (`id` is the comment id). Author only, while EM ANDAMENTO."""
        data = _valid(CommentUpdateSerializer, request.data)
        comment = services.edit_comment(
            authenticated_user(request), _id_param(request), data["comment"]
        )
        return Response(CommentSerializer(comment).data)

from rest_framework import permissions, views
from forms.serializers import *
from forms.models import *
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from core.permissions import *
import core.utils as forms_utils
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


# ParentForm API
class ParentFormViewAPI(views.APIView):
    """
    Allows a parent to submit a form with their information and their child's information.

    The form is saved with the parent's email, so that the staff can contact them.
    A staff cannot submit a form on behalf of a parent, unless they are a parent themselves.
    """

    permission_classes = [permissions.IsAuthenticated & (IsDomBoscoStaff | IsDomBoscoParent | IsDomBoscoAdmin)]

    @swagger_auto_schema(responses={200: ParentsFormSerializer(many=True)}, query_serializer=ParentQuerySerializer)
    def get(self, request: Request):
        """
        Returns a list of all forms submitted by parents.

        If the user is a staff member, they can see all forms assigned to them and all forms that are unassigned (PENDING).
        If the user is a parent, they can only see the forms they have submitted.
        """

        if forms_utils.is_superuser(request.user):
            # If the user is a superuser, they can see all forms
            parents_forms = ParentForm.objects.all()
        elif forms_utils.is_dom_bosco_staff(request.user, include_superuser=True):
            # If the user is a staff member, they can see all forms assigned to them
            # and all forms that are unassigned (PENDING)
            unassigned = Q(status=ParentForm.StatusChoices.PENDENTE)
            assigned_to_current_user = Q(staffform__assigned_staff=request.user)
            parents_forms = ParentForm.objects.filter(unassigned | assigned_to_current_user)
        elif forms_utils.is_parent(request.user):
            # If the user is a parent, they can only see the forms they submitted
            parents_forms = ParentForm.objects.filter(responsible_party=request.user)
        else:
            # If the user is not a parent or a staff member, they cannot see any forms
            return Response(
                data={"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if request.query_params.get("id"):
            try:
                parent_form = ParentForm.objects.get(id=request.query_params["id"])
            except ParentForm.DoesNotExist:
                return Response(
                    data={"detail": "Parent form not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            serializer = ParentsFormSerializer(parent_form)
            return Response(serializer.data)

        if request.query_params.get("status"):
            parents_forms = parents_forms.filter(status=request.query_params["status"])

        if request.query_params.get("assigned_staff"):
            parents_forms = parents_forms.filter(staffform__assigned_staff__email=request.query_params["assigned_staff"])
        
        if request.query_params.get("responsible_party"):
            parents_forms = parents_forms.filter(responsible_party__email=request.query_params["responsible_party"])

        serializer = ParentsFormSerializer(parents_forms.order_by("status", "created_at"), many=True)
        return Response(serializer.data)

    @swagger_auto_schema(responses={201: ParentsFormSerializer()}, request_body=ParentsFormSerializer)
    def post(self, request: Request):
        """
        Allows a parent to submit a form with their information and their child's information.

        The form is saved with the parent's email, so that the staff can contact them.
        A staff cannot submit a form on behalf of a parent, unless they are a parent themselves.
        """

        if not forms_utils.is_parent(request.user, include_superuser=True):
            return Response(
                data={"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ParentsFormSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(responses={200: ParentsFormSerializer()}, query_serializer=ParentQuerySerializer)
    def delete(self, request: Request):
        """
        Allows a parent to delete a form they submitted.

        A parent cannot delete a form that has been already assigned to a staff member,
        unless they are a superuser.
        """
        _id = request.query_params.get("id")
        if not _id:
            return Response(
                data={"detail": "You must provide the id parameter."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            parent_form = ParentForm.objects.get(id=_id)
        except ParentForm.DoesNotExist:
            return Response(
                data={"detail": "Parent form not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if (
            parent_form.status == ParentForm.StatusChoices.PENDENTE
            and parent_form.responsible_party == request.user
            or forms_utils.is_superuser(request.user)
        ):
            parent_form.delete()
            return Response(status=status.HTTP_200_OK)
        return Response(
            data={"detail": "You do not have permission to perform this action."},
            status=status.HTTP_403_FORBIDDEN,
        )

    @swagger_auto_schema(responses={200: ParentsFormSerializer()}, request_body=ParentsFormSerializer)
    def put(self, request: Request):
        """
        Allows a parent to update a form they submitted.

        A form cannot be updated if it's already finished or cancelled.
        """

        _id = request.query_params.get("id")
        if not _id:
            return Response(
                data={"detail": "You must provide the id parameter."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            parent_form = ParentForm.objects.get(id=_id)
        except ParentForm.DoesNotExist:
            return Response(
                data={"detail": "Parent form not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if (
            parent_form.responsible_party != request.user
            and not forms_utils.is_superuser(request.user)
            or parent_form.status > ParentForm.StatusChoices.ANDAMENTO
        ):
            return Response(
                data={"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ParentsFormSerializer(
            parent_form,
            data=request.data,
            context={"request": request},
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ParentFormsChoicesViewAPI(views.APIView):
    """
    Returns the choices for the parent form fields as a dictionary
    to be handled by the frontend.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request):
        """
        Returns a list of all choices for the parent form.

        The choices are returned as a dictionary to be handled by the frontend.
        """

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

    def put(self, request: Request):
        """
        Allows a staff member to update the status of a parent form.

        A parent cannot update the status of a form.
        A staff member can only update the status to a higher status.

        The status can be one of the following:
            0 - PENDENTE
            1 - EM ANDAMENTO
            2 - FINALIZADO
            3 - CANCELADO

        """

        if not forms_utils.is_dom_bosco_staff(request.user, include_superuser=True):
            return Response(
                data={"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

        _id = request.query_params.get("id")
        if not _id:
            return Response(
                data={"detail": "You must provide the id parameter."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            parent_form = ParentForm.objects.get(id=_id)
        except ParentForm.DoesNotExist:
            return Response(
                data={"detail": "Parent form not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if parent_form.status >= request.data["status"] and not forms_utils.is_superuser(request.user):
            return Response(
                data={"detail": "You cannot change the status to a previous status."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        parent_form.status = request.data["status"]
        parent_form.save()
        return Response(
            data={
                "id": parent_form.id,
                "status": parent_form.status,
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

    def get(self, request: Request):
        """
        Returns a list of all forms submitted by staff members.

        If the user is a staff member, they can see all forms they submitted.
        If the user is a parent, they can see all forms submitted by staff members assigned to their forms.
        """
        if forms_utils.is_superuser(request.user):
            staff_forms = StaffForm.objects.all()
        elif forms_utils.is_parent(request.user):
            staff_forms = StaffForm.objects.filter(parent_form__responsible_party=request.user)
        elif forms_utils.is_dom_bosco_staff(request.user):
            staff_forms = StaffForm.objects.filter(assigned_staff=request.user)
        else:
            return Response(
                data={"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = StaffFormSerializer(staff_forms.order_by("-created_at"), many=True)
        return Response(serializer.data)

    def post(self, request: Request):
        """
        Allows a staff member to answer a form submitted by a parent.

        The form is saved with the staff member's email, so that the parent can contact them.
        Once a staff member submits a form, the status of the parent form is updated to "EM ANDAMENTO".
        Only staff members can submit a form.
        """

        if not forms_utils.is_dom_bosco_staff(request.user, include_superuser=True):
            return Response(
                data={"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = StaffFormSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            staff_form: StaffForm = serializer.save()
            staff_form.parent_form.status = ParentForm.StatusChoices.ANDAMENTO
            staff_form.parent_form.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def delete(self, request: Request):
    #     """
    #     Allows a staff member to delete a form they submitted
    #     """
    #     _id = request.query_params.get("id")
    #     if not _id:
    #         return Response(
    #             data={"detail": "You must provide the id parameter."},
    #             status=status.HTTP_400_BAD_REQUEST,
    #         )

    #     try:
    #         staff_form = StaffForm.objects.get(id=_id)
    #     except StaffForm.DoesNotExist:
    #         return Response(
    #             data={"detail": "Staff form not found."},
    #             status=status.HTTP_404_NOT_FOUND,
    #         )

    #     if staff_form.assigned_staff == request.user or forms_utils.is_superuser(request.user):
    #         staff_form.delete()
    #         return Response(status=status.HTTP_200_OK)
    #     return Response(
    #         data={"detail": "You do not have permission to perform this action."},
    #         status=status.HTTP_403_FORBIDDEN,
    #     )

    def put(self, request: Request):
        """
        Allows a staff member to update a form they submitted.

        A staff form cannot be updated if it's already finished or cancelled.
        """

        _id = request.query_params.get("id")
        if not _id:
            return Response(
                data={"detail": "You must provide the id parameter."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            staff_form = StaffForm.objects.get(id=_id)
        except StaffForm.DoesNotExist:
            return Response(
                data={"detail": "Staff form not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if (
            staff_form.assigned_staff != request.user
            and not forms_utils.is_superuser(request.user)
            or staff_form.parent_form.status > ParentForm.StatusChoices.ANDAMENTO
        ):
            return Response(
                data={"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = StaffFormSerializer(staff_form, data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentViewAPI(views.APIView):
    """
    Allows a user to add, update, or delete a comment on a form they submitted or are assigned to.

    A user can only delete or update their own comments, unless they are a superuser.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request):
        """
        Allows a user to add a comment to a form.

        A user can only add a comment to a form they submitted or are assigned to.
        """
        serializer = CommentSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request: Request):
        """
        Returns a list of all comments for a form.

        A user can only see comments for a form they submitted or are assigned to.
        """
        _id = request.query_params.get("id")
        if not _id:
            return Response(
                data={"detail": "You must provide the id parameter."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            parent_form = ParentForm.objects.get(id=_id)
            if not forms_utils.has_comment_permission(request.user, parent_form):
                return Response(
                    data={"detail": "You do not have permission to perform this action."},
                    status=status.HTTP_403_FORBIDDEN,
                )
        except ParentForm.DoesNotExist:
            return Response(
                data={"detail": "Form not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        comments = Comment.objects.filter(parent_form_id=_id)
        serializer = CommentSerializer(comments.order_by("created_at"), many=True)

        return Response(serializer.data)

    def delete(self, request: Request):
        """
        Allows a user to delete a comment.

        A user can only delete their own comments, unless they are a superuser, and the form is still in progress.
        """
        _id = request.query_params.get("id")
        if not _id:
            return Response(
                data={"detail": "You must provide the id parameter."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            comment = Comment.objects.get(id=_id)
        except Comment.DoesNotExist:
            return Response(
                data={"detail": "Comment not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        if (comment.user == request.user and comment.parent_form.status == ParentForm.StatusChoices.ANDAMENTO) or forms_utils.is_superuser(
            request.user
        ):
            comment.delete()
            return Response(status=status.HTTP_200_OK)
        return Response(
            data={"detail": "You do not have permission to perform this action."},
            status=status.HTTP_403_FORBIDDEN,
        )

    def put(self, request: Request):
        """
        Allows a user to update a comment.

        A user can only update their own comments, unless they are a superuser, and the form is still in progress.
        """

        _id = request.query_params.get("id")
        if not _id:
            return Response(
                data={"detail": "You must provide the id parameter."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            comment = Comment.objects.get(id=_id)
        except Comment.DoesNotExist:
            return Response(
                data={"detail": "Comment not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        if (
            comment.user != request.user
            and not forms_utils.is_superuser(request.user)
            or comment.parent_form.status != ParentForm.StatusChoices.ANDAMENTO
        ):
            return Response(
                data={"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = CommentSerializer(comment, data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

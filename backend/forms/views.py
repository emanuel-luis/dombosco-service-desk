from rest_framework import permissions, views
from forms.serializers import *
from forms.models import ParentForm, StaffForm
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
import forms.utils as forms_utils


# ParentForm API
class ParentsFormViewAPI(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request):
        """
        Returns a list of all forms submitted by parents.

        If the user is a staff member, they can see all forms submitted by parents.
        If the user is a parent, they can only see the forms they submitted
        """
        if forms_utils.is_superuser(request.user):
            parents_forms = ParentForm.objects.all()
        elif forms_utils.is_dom_bosco_staff(request.user, include_superuser=True):
            unassigned = Q(status=ParentForm.StatusChoices.PENDENTE)
            assigned_to_current_user = Q(staffform__assigned_staff=request.user)
            parents_forms = ParentForm.objects.filter(unassigned | assigned_to_current_user)
        else:
            parents_forms = ParentForm.objects.filter(responsible_party=request.user)

        if request.query_params.get("id"):
            parents_forms = parents_forms.filter(id=request.query_params["id"])
            return Response(ParentsFormSerializer(parents_forms.first()).data)

        if request.query_params.get("status"):
            parents_forms = parents_forms.filter(status=request.query_params["status"])

        serializer = ParentsFormListSerializer(parents_forms.order_by("status", "created_at"), many=True)
        return Response(serializer.data)

    def post(self, request: Request):
        """
        Allows a parent to submit a form with their information and their child's information.

        The form is saved with the parent's email, so that the staff can contact them.
        A staff cannot submit a form on behalf of a parent, unless they are a parent themselves.
        """

        serializer = ParentsFormSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request: Request):
        """
        Allows a parent to delete a form they submitted.
        A staff member can delete any form.
        """
        _id = request.query_params.get("id")
        if not _id:
            return Response(data={"detail": "You must provide the id parameter."}, status=status.HTTP_400_BAD_REQUEST)
        
        parent_form = ParentForm.objects.get(id=_id)
        if parent_form.responsible_party == request.user or forms_utils.is_superuser(request.user):
            parent_form.delete()
            return Response(status=status.HTTP_200_OK)
        return Response(data={"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)

    def put(self, request: Request):
        """
        Allows a parent to update a form they submitted.
        A staff member can update any form.
        """

        _id = request.query_params.get("id")
        if not _id:
            return Response(data={"detail": "You must provide the id parameter."}, status=status.HTTP_400_BAD_REQUEST)
        
        parent_form = ParentForm.objects.get(id=_id)
        if parent_form.responsible_party != request.user and not forms_utils.is_superuser(request.user):
            return Response(data={"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)

        serializer = ParentsFormSerializer(parent_form, data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdateStatusParentsFormAPI(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def put(self, request: Request):
        if not forms_utils.is_dom_bosco_staff(request.user, include_superuser=True):
            return Response(data={"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        
        _id = request.query_params.get("id")
        if not _id:
            return Response(data={"detail": "You must provide the id parameter."}, status=status.HTTP_400_BAD_REQUEST)
        
        parent_form = ParentForm.objects.get(id=_id)
        if parent_form.status >= request.data["status"] and not forms_utils.is_superuser(request.user):
            return Response(data={"detail": "You cannot change the status to a previous status."}, status=status.HTTP_400_BAD_REQUEST)
        parent_form.status = request.data["status"]
        parent_form.save()
        return Response(status=status.HTTP_200_OK)

# StaffForm API
class StaffFormViewAPI(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request: Request):
        """
        Returns a list of all forms submitted by staff.

        If the user is a staff member, they can see all forms submitted by staff.
        If the user is a parent, they can only see the forms they submitted
        """
        if forms_utils.is_superuser(request.user):
            staff_forms = StaffForm.objects.all()
        elif forms_utils.is_parent(request.user):
            staff_forms = StaffForm.objects.filter(parentform__responsible_party=request.user)
        elif forms_utils.is_dom_bosco_staff(request.user):
            staff_forms = StaffForm.objects.filter(assigned_staff=request.user)
        else:
            return Response(data={"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        serializer = StaffFormSerializer(staff_forms.order_by("-created_at"), many=True)
        return Response(serializer.data)

    def post(self, request: Request):
        """
        Allows a staff member to submit a form with their information and their child's information.

        The form is saved with the staff member's email, so that the staff can contact them.
        A parent cannot submit a form on behalf of a staff member, unless they are a staff member themselves.
        """

        if not forms_utils.is_dom_bosco_staff(request.user, include_superuser=True):
            return Response(data={"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)

        serializer = StaffFormSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            staff_form: StaffForm = serializer.save()
            staff_form.parent_form.status = ParentForm.StatusChoices.ANDAMENTO
            staff_form.parent_form.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request: Request):
        """
        Allows a staff member to delete a form they submitted.
        A parent can delete any form.
        """
        _id = request.query_params.get("id")
        if not _id:
            return Response(data={"detail": "You must provide the id parameter."}, status=status.HTTP_400_BAD_REQUEST)
        
        staff_form = StaffForm.objects.get(id=_id)
        if staff_form.assigned_staff == request.user or forms_utils.is_superuser(request.user):
            staff_form.delete()
            return Response(status=status.HTTP_200_OK)
        return Response(data={"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
    
    def put(self, request: Request):
        """
        Allows a staff member to update a form they submitted.
        A parent can update any form.
        """

        _id = request.query_params.get("id")
        if not _id:
            return Response(data={"detail": "You must provide the id parameter."}, status=status.HTTP_400_BAD_REQUEST)
        
        staff_form = StaffForm.objects.get(id=_id)
        if staff_form.assigned_staff != request.user and not forms_utils.is_superuser(request.user):
            return Response(data={"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)

        serializer = StaffFormSerializer(staff_form, data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
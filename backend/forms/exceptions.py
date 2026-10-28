"""Domain errors raised by forms.services.

They are APIExceptions, so DRF renders them as {"detail": ...} with the right status
without every view having to catch them.
"""

from rest_framework import status
from rest_framework.exceptions import APIException


class RequestForbidden(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "You do not have permission to perform this action."
    default_code = "forbidden"


class RequestNotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Not found."
    default_code = "not_found"


class RequestConflict(APIException):
    """The request is in a state that does not allow the operation."""

    status_code = status.HTTP_409_CONFLICT
    default_detail = "The request is not in a state that allows this operation."
    default_code = "conflict"


class RequestInvalid(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Invalid input."
    default_code = "invalid"

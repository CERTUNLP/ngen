from django.core.exceptions import ValidationError

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

# https://github.com/encode/django-rest-framework/discussions/7850

def django_error_handler(exc, context):
    """Handle django core's errors."""
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if response is None and isinstance(exc, ValidationError):
        return Response(status=status.HTTP_400_BAD_REQUEST, data=exc.message_dict)

    return response

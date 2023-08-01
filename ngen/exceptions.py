from django.core.exceptions import ValidationError as core_ValidationError

from rest_framework.exceptions import ValidationError
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError

# https://github.com/encode/django-rest-framework/discussions/7850

def django_error_handler(exc, context):
    """Handle django core's errors."""
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if response is None and isinstance(exc, core_ValidationError):
        return Response(status=status.HTTP_400_BAD_REQUEST, data=exc.message_dict)

    elif response is None and isinstance(exc, IntegrityError):
        error_message = str(exc)
        # duplicate key value violates unique constraint \"network_entity_slug_key\"\nDETAIL:  Key (slug)=(test) already exists.\n
        if 'duplicate key value violates unique constraint' in error_message:
            try:
                key = error_message.split('Key (')[1].split(')')[0].strip()
                value = error_message.split(')=(')[1].split(')')[0].strip()
                return Response(status=status.HTTP_400_BAD_REQUEST, data={key: [f'Ya existe una entidad de red con {key}={value}.'], '_detail': error_message})
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': [error_message]})
        elif 'update or delete on table' in error_message and 'violates foreign key constraint' in error_message:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'__all__': [f'No se puede editar y/o eliminar la entidad de red porque hay objetos que dependen de ella.'], '_detail': error_message})
        else:
            # update or delete on table \"network_entity\" violates foreign key constraint \"network_network_entity_id_01d78cbb_fk_network_entity_id\" on table \"network\"\nDETAIL:  Key (id)=(2) is still referenced from table \"network\".\n
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': [error_message]})

    return response

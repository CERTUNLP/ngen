from django.apps import AppConfig
from rest_framework.pagination import PageNumberPagination


class NgenConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ngen'

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100

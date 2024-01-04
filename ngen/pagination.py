from rest_framework.pagination import PageNumberPagination
from constance import config


class CustomPagination(PageNumberPagination):
    page_size_query_param = 'page_size'

    @property
    def page_size(self):
        return getattr(config, 'PAGE_SIZE', 10)

    @property
    def max_page_size(self):
        return getattr(config, 'PAGE_SIZE_MAX', 100)

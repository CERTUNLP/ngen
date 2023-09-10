# pylint: disable=locally-disabled, missing-class-docstring, too-few-public-methods
"""
Filters for ngen models.
"""
import django_filters
from django_filters import DateFilter, DateFromToRangeFilter
from ngen.models import Taxonomy


class BaseFilter(django_filters.FilterSet):
    """
    Base filter.
    Allows to filter by:
        - exact id
        - exact created date
        - range created date
        - exact modified date
        - range modified date
    """
    id = django_filters.NumberFilter()

    created = DateFilter(field_name='created', lookup_expr='exact')
    created_range = DateFromToRangeFilter(field_name='created')

    modified = DateFilter(field_name='modified', lookup_expr='exact')
    modified_range = DateFromToRangeFilter(field_name='modified')


class TaxonomyFilter(BaseFilter):
    """
    Taxonomy model filter.
    Allows to filter by:
        - name (icontains)
        - slug (icontains)
        - description (icontains)
        - active (exact)
        - type (exact)
        - parent (exact, isnull)
    """
    class Meta:
        model = Taxonomy
        fields = {
            'name': ['icontains'],
            'slug': ['icontains'],
            'description': ['icontains'],
            'active': ['exact'],
            'type': ['exact'],
            'parent': ['exact', 'isnull'],
        }

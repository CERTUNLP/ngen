# pylint: disable=locally-disabled, missing-class-docstring, too-few-public-methods
"""
Filters for ngen models.
"""
import django_filters
from django_filters import DateFilter, DateFromToRangeFilter
from ngen.models import Taxonomy, Event, Case


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


class NgenAddressModelFilter(BaseFilter):
    """
    NgenAddressModel model filter.
    Allows to filter by:
        - cidr (exact)
        - domain (exact)
        - is_subnet_of (net_contained_or_equal)
        - is_subdomain_of (domain_is_subdomain_of)
    """
    cidr = django_filters.CharFilter(field_name='cidr', lookup_expr='exact')
    domain = django_filters.CharFilter(
        field_name='domain', lookup_expr='exact')

    is_subnet_of = django_filters.CharFilter(
        field_name='cidr',
        lookup_expr='net_contained_or_equal',
        label='Is subnet of'
    )
    is_subdomain_of = django_filters.CharFilter(
        field_name='domain',
        method='domain_is_subdomain_of',
        label='Is subdomain of'
    )

    def domain_is_subdomain_of(self, queryset, name, value):
        """
        Filter by subdomain.
        """
        return queryset.filter(domain__endswith=f'.{value}')


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


class EventFilter(NgenAddressModelFilter):
    """
    Event model filter.
    Allows to filter by:
        - date (exact)
        - feed (exact)
        - tlp (exact)
        - priority (exact)
        - taxonomy (exact)
        - parent (exact, isnull)
        - case (exact, isnull)
        - reporter (exact)
        - uuid (exact)
        - inherits NgenAddressModelFilter
    """

    class Meta:
        model = Event
        fields = {
            'date': ['exact'],
            'feed': ['exact'],
            'tlp': ['exact'],
            'priority': ['exact'],
            'taxonomy': ['exact'],
            'parent': ['exact', 'isnull'],
            'case': ['exact', 'isnull'],
            'reporter': ['exact'],
            'uuid': ['exact']
        }


class CaseFilter(BaseFilter):
    """
    Event model filter.
    Allows to filter by:
        - date (exact, range)
        - attend_date (exact, range)
        - solve_date (exact, range)
        - lifecycle (exact)
        - priority (exact)
        - tlp (exact)
        - casetemplate_creator (exact)
        - uuid (exact)
        - parent (exact, isnull)
        - assigned (exact, isnull)
        - state (exact)
    """

    date_range = DateFromToRangeFilter(field_name='created')
    attend_date_range = DateFromToRangeFilter(field_name='attend_date')
    solve_date_range = DateFromToRangeFilter(field_name='solve_date')

    class Meta:
        model = Case
        fields = {
            'date': ['exact'],
            'attend_date': ['exact'],
            'solve_date': ['exact'],
            'lifecycle': ['exact'],
            'priority': ['exact'],
            'tlp': ['exact'],
            'casetemplate_creator': ['exact'],
            'uuid': ['exact'],
            'parent': ['exact', 'isnull'],
            'assigned': ['exact', 'isnull'],
            'state': ['exact'],
        }

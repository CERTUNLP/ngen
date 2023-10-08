# pylint: disable=locally-disabled, missing-class-docstring, too-few-public-methods
"""
Filters for ngen models.
"""
import django_filters
from django_filters import DateFilter, DateFromToRangeFilter
from ngen.models import Taxonomy, Event, Case, Feed, Tlp, Priority, User, CaseTemplate


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


class NgenAddressModelFilter(django_filters.FilterSet):
    """
    NgenAddressModel model filter.
    Allows to filter by:
        - cidr (exact)
        - domain (exact)
        - is_subnet_of (net_contained_or_equal)
        - is_subdomain_of (domain_is_equal_or_subdomain_of)
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
        return queryset.filter(domain__endswith=value)


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


class EventFilter(BaseFilter, NgenAddressModelFilter):
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
        - event cidr (net_contained_or_equal)
        - event domain (endswith)
    """

    date_range = DateFromToRangeFilter(field_name='date')
    attend_date_range = DateFromToRangeFilter(field_name='attend_date')
    solve_date_range = DateFromToRangeFilter(field_name='solve_date')

    event_cidr = django_filters.CharFilter(
        label='Event cidr', method='filter_by_cidr')
    event_domain = django_filters.CharFilter(
        label='Event domain', method='filter_by_domain')

    def filter_by_cidr(self, queryset, name, value):
        """
        Filter by cidr.
        """
        return queryset.filter(events__cidr__net_contained_or_equal=value)

    def filter_by_domain(self, queryset, name, value):
        """
        Filter by domain, matches a domain or subdomains.
        """
        return queryset.filter(events__domain__endswith=value)

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


class FeedFilter(BaseFilter):
    """
    Feed model filter.
    Allows to filter by:
        - name (icontains)
        - slug (icontains)
        - description (icontains)
        - active (exact)
    """

    class Meta:
        model = Feed
        fields = {
            'name': ['icontains'],
            'slug': ['icontains'],
            'description': ['icontains'],
            'active': ['exact']
        }


class TlpFilter(BaseFilter):
    """
    Tlp model filter.
    Allows to filter by:
        - when (icontains)
        - why (icontains)
        - information (icontains)
        - description (icontains)
        - encrypt (exact)
        - name (icontains)
        - slug (icontains)
        - code (exact)
    """

    class Meta:
        model = Tlp
        fields = {
            'when': ['icontains'],
            'why': ['icontains'],
            'information': ['icontains'],
            'description': ['icontains'],
            'encrypt': ['exact'],
            'name': ['icontains'],
            'slug': ['icontains'],
            'code': ['exact']
        }


class PriorityFilter(BaseFilter):
    """
    Priority model filter.
    Allows to filter by:
        - name (icontains)
        - slug (icontains)
        - severity (exact)
        - attend_time (exact)
        - solve_time (exact)
        - notification_amount (exact)
    """

    class Meta:
        model = Priority
        fields = {
            'name': ['icontains'],
            'slug': ['icontains'],
            'severity': ['exact'],
            'attend_time': ['exact'],
            'solve_time': ['exact'],
            'notification_amount': ['exact']
        }


class UserFilter(BaseFilter):
    """
    User model filter.
    Allows to filter by:
        - username (icontains)
        - email (icontains)
        - first_name (icontains)
        - last_name (icontains)
        - is_superuser (exact)
        - is_staff (exact)
        - is_active (exact)
        - date_joined (exact)
        - last_login (exact)
    """

    class Meta:
        model = User
        fields = {
            'username': ['icontains'],
            'email': ['icontains'],
            'first_name': ['icontains'],
            'last_name': ['icontains'],
            'is_superuser': ['exact'],
            'is_staff': ['exact'],
            'is_active': ['exact'],
            'date_joined': ['exact'],
            'last_login': ['exact'],
        }


class CaseTemplateFilter(BaseFilter, NgenAddressModelFilter):
    """
    Template model filter.
    Allows to filter by:
        - case_lifecycle (exact)
        - active (exact)
        - priority (exact)
        - event_taxonomy (exact)
        - event_feed (exact)
        - case_tlp (exact)
        - case_state (exact)
        - inherits NgenAddressModelFilter
    """

    class Meta:
        model = CaseTemplate
        fields = {
            'case_lifecycle': ['exact'],
            'active': ['exact'],
            'priority': ['exact'],
            'event_taxonomy': ['exact'],
            'event_feed': ['exact'],
            'case_tlp': ['exact'],
            'case_state': ['exact'],
        }

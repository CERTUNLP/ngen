"""
Dashboard Presenter
"""
from datetime import datetime, timedelta
from django.db.models import Count, Q
from ngen.models.administration import Feed

from ngen.models.auth import User
from ngen.models.case import Case, Event
from ngen.models.constituency import NetworkEntity


class DashboardPresenter:
    """
    Presenter to organize Dashboard logic.
    """

    QUERY_LIMIT = 10

    def __init__(self, request):
        self.request = request

        self.date_from = None
        self.date_to = None

        self.current_user = None
        self.cases = None
        self.cases_limited = None
        self.events = None
        self.events_limited = None
        self.feeds = None
        self.network_entities = None

    def get_date_from(self):
        """
        Get the date_from
        """
        if not self.date_from:
            self.date_from = self.parse_date(
                self.get_query_param("date_from")
            ) or datetime.now() - timedelta(days=30)

        return self.date_from

    def get_date_to(self):
        """
        Get the date_to
        """
        if not self.date_to:
            self.date_to = (
                self.parse_date(self.get_query_param("date_to")) or datetime.now()
            )

        return self.date_to

    def get_current_user(self):
        """
        Get the current user.
        """
        if not self.current_user:
            self.current_user = User.objects.get(pk=self.request.user.id)

        return self.current_user

    def get_cases(self):
        """
        Get cases.
        """
        if not self.cases:
            self.cases = Case.objects.filter(
                date__range=(self.get_date_from(), self.get_date_to())
            )

            if not self.get_current_user().is_superuser:
                self.cases = self.cases.filter(assigned_to=self.current_user)

        return self.cases

    def get_cases_limited(self):
        """
        Get cases limited to self.QUERY_LIMIT.
        """

        return self.get_cases()[: self.QUERY_LIMIT]

    def get_events(self):
        """
        Get events.
        """
        if not self.events:
            self.events = Event.objects.filter(
                date__range=(self.get_date_from(), self.get_date_to()),
                parent__isnull=True,
            )

        return self.events

    def get_events_limited(self):
        """
        Get events limited to self.QUERY_LIMIT.
        """

        return self.get_events()[: self.QUERY_LIMIT]

    def get_feeds(self):
        """
        Get the Feeds, the number of events they are involved in and the total amount of events.
        """
        feed_count = Feed.objects.annotate(
            event_count=Count("event", filter=Q(event__in=self.get_events()))
        ).order_by("-event_count")

        total_events_count = self.get_events().count()

        feed_in_events = []
        for feed in feed_count:
            feed_in_events.append(
                {"feed_name": feed.name, "event_count": feed.event_count}
            )

        feeds = {
            "total_events_count": total_events_count,
            "feeds_in_events": feed_in_events,
        }

        return feeds

    def get_network_entities(self):
        """
        Get Network Entities with their networks prefetched.
        """
        if not self.network_entities:
            self.network_entities = NetworkEntity.objects.prefetch_related(
                "networks"
            ).all()

        return self.network_entities

    def are_dates_valid(self):
        """
        Check if the dates are valid.
        """
        return self.get_date_from() <= self.get_date_to()

    def get_query_param(self, param_name, default=None, data_type=str):
        """
        Get a certain query parameter from the request.
        """
        value = self.request.GET.get(param_name, default)

        if value is not None:
            try:
                return data_type(value)
            except (ValueError, TypeError):
                return None
        return value

    def parse_date(self, date_string, date_format="%Y-%m-%d") -> datetime or None:
        """
        Return a datetime object from a date string.
        """
        try:
            return datetime.strptime(date_string, date_format)
        except (ValueError, TypeError):
            return None

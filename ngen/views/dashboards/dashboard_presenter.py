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

        self.date_from = self.get_date_from()
        self.date_to = self.get_date_to()

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
        param_date = self.get_query_param("date_from")
        if not param_date:
            return datetime.now() - timedelta(days=30)

        return self.parse_date(param_date, "date_from")

    def get_date_to(self):
        """
        Get the date_to
        """
        param_date = self.get_query_param("date_to")
        if not param_date:
            return datetime.now()

        return self.parse_date(param_date, "date_to")

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
            cases = Case.objects.prefetch_related("events")
            self.cases = cases.filter(date__range=(self.date_from, self.date_to))

            # this must be in other endpoint
            # if not self.get_current_user().is_superuser:
            #     self.cases = self.cases.filter(assigned=self.current_user)

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
                date__range=(self.date_from, self.date_to),
                parent__isnull=True,
            ).order_by("-date")

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
            events_count=Count("events", filter=Q(events__in=self.get_events()))
        ).order_by("-events_count")

        total_events_count = self.get_events().count()

        feed_in_events = []
        for feed in feed_count:
            feed_in_events.append(
                {"feed_name": feed.name, "events_count": feed.events_count}
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

    def is_date_range_valid(self):
        """
        Check if the date range is valid.
        """
        return self.date_from <= self.date_to

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

    def parse_date(
        self, date_string, param_name, date_format="%Y-%m-%dT%H:%M:%SZ"
    ) -> datetime:
        """
        Return a datetime object from a date string.
        """
        try:
            return datetime.strptime(date_string, date_format)
        except ValueError as exc:
            raise ValueError(
                f"Invalid '{param_name}' format. Use YYYY-MM-DDTHH:MM:SSZ"
            ) from exc


class NetworkAdminDashboardPresenter(DashboardPresenter):
    """
    Presenter to organize Network Admin Dashboard logic.
    """

    def get_events(self):
        return (
            super().get_events().filter(network__contacts__user=self.get_current_user())
        )

    def get_cases(self):
        return (
            super()
            .get_cases()
            .filter(events__network__contacts__user=self.get_current_user())
        )

    def get_network_entities(self):
        """
        Get Network Entities with their networks prefetched.
        """
        if not self.network_entities:
            self.network_entities = (
                NetworkEntity.objects.prefetch_related("networks")
                .filter(networks__contacts__user=self.get_current_user())
                .distinct()
            )

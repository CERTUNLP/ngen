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

        self.current_user = User.objects.get(pk=request.user.id)
        self.cases = self.get_cases()
        self.cases_limited = self.cases[: self.QUERY_LIMIT]
        self.events = self.get_events()
        self.events_limited = self.events[: self.QUERY_LIMIT]
        self.feeds = self.get_feeds()
        self.network_entities = self.get_network_entities()

    def get_date_from(self):
        """
        Get the date_from
        """
        return self.parse_date(
            self.get_query_param(self.request, "date_from")
        ) or datetime.now() - timedelta(days=30)

    def get_date_to(self):
        """
        Get the date_to
        """
        return (
            self.parse_date(self.get_query_param(self.request, "date_to"))
            or datetime.now()
        )

    def get_cases(self):
        """
        Get cases.
        """
        cases = Case.objects.filter(created__range=(self.date_from, self.date_to))

        if not self.current_user.is_superuser:
            cases = cases.filter(assigned_to=self.current_user)

        return cases

    def get_events(self):
        """
        Get events.
        """
        events = Event.objects.filter(
            created__range=(self.date_from, self.date_to), parent__isnull=True
        )

        return events

    def get_feeds(self):
        """
        Get the Feeds, the number of events they are involved in and the total amount of events.
        """
        feed_count = Feed.objects.annotate(
            event_count=Count("event", filter=Q(event__in=self.events))
        ).order_by("-event_count")

        total_events_count = self.events.count()

        feed_in_events = []
        for feed in feed_count:
            feed_in_events.append(
                {"feed_name": feed.name, "event_count": feed.event_count}
            )

        feeds = {
            "total_events": total_events_count,
            "feeds_in_events": feed_in_events,
        }

        return feeds

    def get_network_entities(self):
        """
        Get Network Entities with their networks prefetched.
        """
        return NetworkEntity.objects.prefetch_related("networks").all()

    def are_dates_valid(self):
        """
        Check if the dates are valid.
        """
        return self.date_from <= self.date_to

    def get_query_param(self, request, param_name, default=None, data_type=str):
        """
        Get a certain query parameter from the request.
        """
        value = request.GET.get(param_name, default)

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

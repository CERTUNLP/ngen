"""
Helper methods for the dashboard.
"""
from datetime import datetime
from django.db.models import Count
from ngen.models import Event, Feed


def get_feed_data():
    """
    Get the amount of Feeds involved in events.
    """
    feed_count = Feed.objects.annotate(event_count=Count("event")).order_by(
        "-event_count"
    )

    total_events = Event.objects.count()

    feed_in_events = []
    for feed in feed_count:
        feed_in_events.append({"feed_name": feed.name, "event_count": feed.event_count})

    feed_data = {"total_events": total_events, "feeds_in_events": feed_in_events}

    return feed_data


def get_query_param(request, param_name, default=None, data_type=str):
    """
    Helper to get a certain query parameter from the request.
    """
    value = request.GET.get(param_name, default)

    if value is not None:
        try:
            return data_type(value)
        except (ValueError, TypeError):
            return None
    return value


def parse_date(date_string, date_format="%Y-%m-%d"):
    """
    Helper to parse a date string.
    """
    try:
        return datetime.strptime(date_string, date_format)
    except (ValueError, TypeError):
        return None

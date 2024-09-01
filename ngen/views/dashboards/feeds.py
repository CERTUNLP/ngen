from rest_framework.response import Response

from ngen.serializers.dashboard import FeedDashboardSerializer
from ngen.views.dashboards.dashboard import DashboardView


class DashboardFeedsView(DashboardView):
    """
    APIView for the dashboard feeds.
    """

    def get(self, request):
        """
        GET endpoint for the dashboard feeds.
        """
        response = super().get(request)

        if response.status_code != 200:
            return response

        feeds = self.dashboard_presenter.get_feeds()

        serialized_data = FeedDashboardSerializer(
            {
                "date_from": self.dashboard_presenter.get_date_from(),
                "date_to": self.dashboard_presenter.get_date_to(),
                "total_events_count": feeds["total_events_count"],
                "feeds_in_events": feeds["feeds_in_events"],
            }
        ).data

        return Response(serialized_data, status=200)

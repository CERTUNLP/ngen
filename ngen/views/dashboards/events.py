from ngen.serializers.dashboard import EventDashboardSerializer
from rest_framework.response import Response
from ngen.views.dashboards.dashboard import DashboardView


class DashboardEventsView(DashboardView):
    """
    APIView for the dashboard events.
    """

    def get(self, request):
        """
        GET endpoint for the dashboard events.
        """
        response = super().get(request)

        if response.status_code != 200:
            return response

        serialized_data = EventDashboardSerializer(
            {
                "date_from": self.dashboard_presenter.get_date_from(),
                "date_to": self.dashboard_presenter.get_date_to(),
                "events": self.dashboard_presenter.get_events_limited(),
            },
            context={"request": request},
        ).data

        return Response(serialized_data, status=200)

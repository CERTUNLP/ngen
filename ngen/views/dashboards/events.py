from rest_framework.response import Response

from ngen.permissions import CustomApiViewPermission
from ngen.serializers.dashboard import EventDashboardSerializer
from ngen.views.dashboards.dashboard import DashboardView
from ngen.views.dashboards.dashboard_presenter import NetworkAdminDashboardPresenter


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


class NetworkAdminDashboardEventsView(DashboardEventsView):
    """
    APIView for the network admin dashboard events.
    """

    permission_classes = [CustomApiViewPermission]
    required_permissions = ["ngen.view_dashboard_network_admin"]

    def _get_presenter(self, request):
        """
        Get the presenter.
        """
        return NetworkAdminDashboardPresenter(request)

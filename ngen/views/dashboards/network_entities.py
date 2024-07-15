from ngen.serializers.dashboard import NetworkEntityDashboardSerializer
from rest_framework.response import Response
from ngen.views.dashboards.dashboard import DashboardView


class DashboardNetworkEntitiesView(DashboardView):
    """
    APIView for the dashboard network entities.
    """

    def get(self, request):
        """
        GET endpoint for the dashboard network entities.
        """
        response = super().get(request)

        if response.status_code != 200:
            return response

        serialized_data = NetworkEntityDashboardSerializer(
            {
                "date_from": self.dashboard_presenter.get_date_from(),
                "date_to": self.dashboard_presenter.get_date_to(),
                "network_entities": self.dashboard_presenter.get_network_entities(),
            },
            context={
                "request": request,
                "events": self.dashboard_presenter.get_events(),
                "date_from": self.dashboard_presenter.get_date_from(),
                "date_to": self.dashboard_presenter.get_date_to(),
            },
        ).data

        return Response(serialized_data, status=200)

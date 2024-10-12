from rest_framework.response import Response

from ngen.permissions import CustomApiViewPermission
from ngen.serializers.dashboard import CaseDashboardSerializer
from ngen.views.dashboards.dashboard import DashboardView
from ngen.views.dashboards.dashboard_presenter import NetworkAdminDashboardPresenter


class DashboardCasesView(DashboardView):
    """
    APIView for the dashboard cases.
    """

    def get(self, request):
        """
        GET endpoint for the dashboard cases.
        """
        response = super().get(request)

        if response.status_code != 200:
            return response

        serialized_data = CaseDashboardSerializer(
            {
                "date_from": self.dashboard_presenter.get_date_from(),
                "date_to": self.dashboard_presenter.get_date_to(),
                "cases": self.dashboard_presenter.get_cases_limited(),
            },
            context={"request": request},
        ).data

        return Response(serialized_data, status=200)


class NetworkAdminDashboardCasesView(DashboardCasesView):
    """
    APIView for the network admin dashboard cases.
    """

    permission_classes = [CustomApiViewPermission]
    required_permissions = ["ngen.view_dashboard_network_admin"]

    def _get_presenter(self, request):
        """
        Get the presenter.
        """
        return NetworkAdminDashboardPresenter(request)

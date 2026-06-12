from rest_framework.response import Response
from rest_framework.views import APIView

from ngen.views.dashboards.dashboard_presenter import (
    DashboardPresenter,
    NetworkAdminDashboardPresenter,
)
from ngen.permissions import CustomApiViewPermission


class DashboardView(APIView):
    """
    Parent APIView for the dashboard. Initializes the presenter and validates dates.
    """

    permission_classes = [CustomApiViewPermission]
    required_permissions = ["ngen.view_dashboard"]

    def __init__(self):
        self.dashboard_presenter = None

    def _get_presenter(self, request):
        """
        Get the presenter. Network admin users get a scoped presenter
        that filters data to their associated contacts/networks.
        """
        user = request.user
        if user.is_superuser or user.is_staff:
            return DashboardPresenter(request)
        return NetworkAdminDashboardPresenter(request)

    def get(self, request):
        """
        Parent GET method to initialize presenter and validate dates.
        """
        try:
            self.dashboard_presenter = self._get_presenter(request)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=400)

        if not self.dashboard_presenter.is_date_range_valid():
            return Response(
                {"error": "Invalid date range. 'date_from' must be before 'date_to'"},
                status=400,
            )

        return Response(status=200)

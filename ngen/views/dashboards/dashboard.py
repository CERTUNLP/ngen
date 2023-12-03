from ngen.views.dashboards.dashboard_presenter import DashboardPresenter
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class DashboardView(APIView):
    """
    Parent APIView for the dashboard. Initializes the presenter and validates dates.
    """

    permission_classes = (IsAuthenticated,)

    def __init__(self):
        self.dashboard_presenter = None

    def get(self, request):
        """
        Parent GET method to initialize presenter and validate dates.
        """
        self.dashboard_presenter = DashboardPresenter(request)

        if not self.dashboard_presenter.are_dates_valid():
            return Response(
                {"error": "Invalid dates. 'date_from' must be before 'date_to'"},
                status=400,
            )

        return Response(status=200)

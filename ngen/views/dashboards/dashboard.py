import time
from ngen.serializers import DashboardSerializer
from ngen.views.dashboards.dashboard_presenter import DashboardPresenter
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class DashboardView(APIView):
    """
    APIView for the dashboard.
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        GET endpoint for the dashboard.
        """
        start_time = time.time()
        dashboard_presenter = DashboardPresenter(request)

        if not dashboard_presenter.are_dates_valid():
            return Response(
                {"error": "Invalid dates. 'date_from' must be before 'date_to'"},
                status=400,
            )

        serialized_data = DashboardSerializer(
            {
                "date_from": dashboard_presenter.date_from,
                "date_to": dashboard_presenter.date_to,
                "cases": dashboard_presenter.cases_limited,
                "events": dashboard_presenter.events_limited,
                "feeds": dashboard_presenter.feeds,
            },
            context={
                "request": request,
                "events": dashboard_presenter.events,
                "network_entities": dashboard_presenter.network_entities,
            },
        ).data

        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time: {execution_time} seconds")

        return Response(serialized_data, status=200)

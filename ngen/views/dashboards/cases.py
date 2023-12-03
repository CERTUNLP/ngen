from ngen.serializers.dashboard import CaseDashboardSerializer
from rest_framework.response import Response
from ngen.views.dashboards.dashboard import DashboardView


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

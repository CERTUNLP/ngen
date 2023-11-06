import time
from datetime import datetime, timedelta
from ngen.models import User, Case, Event
from ngen.serializers import DashboardSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ngen.views.dashboards import helpers


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
        date_from = helpers.parse_date(
            helpers.get_query_param(request, "date_from")
        ) or datetime.now() - timedelta(days=30)
        date_to = (
            helpers.parse_date(helpers.get_query_param(request, "date_to"))
            or datetime.now()
        )

        if date_from > date_to:
            return Response({"error": "date_from must be before date_to"}, status=400)

        current_user = User.objects.get(pk=request.user.id)

        cases = Case.objects.filter(created__range=(date_from, date_to))

        if not current_user.is_superuser:
            cases = cases.filter(assigned_to=current_user)

        events = Event.objects.filter(created__range=(date_from, date_to))

        feed_data = helpers.get_feed_data()

        serialized_data = DashboardSerializer(
            {
                "date_from": date_from,
                "date_to": date_to,
                "feed_data": feed_data,
                "cases": cases,
                "events": events,
            },
            context={"request": request},
        )

        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time: {execution_time} seconds")

        return Response(serialized_data.data, status=200)

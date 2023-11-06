from rest_framework import serializers
from ngen.serializers import EventSerializerReduced, CaseSerializerReduced
from ngen.serializers.dashboard_feed import FeedDataSerializer


class DashboardSerializer(serializers.Serializer):
    date_from = serializers.DateTimeField(required=False)
    date_to = serializers.DateTimeField(required=False)
    cases = CaseSerializerReduced(many=True)
    events = EventSerializerReduced(many=True)
    feed_data = FeedDataSerializer()

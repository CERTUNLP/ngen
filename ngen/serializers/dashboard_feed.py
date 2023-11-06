from rest_framework import serializers


class FeedsInEventsSerializer(serializers.Serializer):
    feed_name = serializers.CharField()
    event_count = serializers.IntegerField()


class FeedDataSerializer(serializers.Serializer):
    total_events = serializers.IntegerField()
    feeds_in_events = FeedsInEventsSerializer(many=True)

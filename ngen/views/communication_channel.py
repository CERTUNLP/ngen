"""
Communication channel views
"""

import django_filters
from rest_framework import permissions, filters, viewsets, status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.urls import resolve
from django.core.exceptions import ObjectDoesNotExist
from ngen import models
from ngen.serializers.communication_channel import CommunicationChannelSerializer


class BaseCommunicationChannelsViewSet(viewsets.ModelViewSet):
    """
    Class that adds communication channel endpoints to canalizable models
    e.g.:
    /api/case/1/communication_channels/
    /api/case/1/communication_channels/1
    /api/event/2/communication_channels/3
    """

    def get_serializer_class(self):
        """
        Get the serializer class.
        Use CommunicationChannelSerializer if the path corresponds to a communication channel view
        """
        if self.is_in_communication_channel_path(self.request.path):
            return CommunicationChannelSerializer

        return self.serializer_class

    @action(detail=True, methods=["get"], url_path="communication_channels")
    def communication_channels(self, request, pk=None):
        """
        View for list of communication channels of a canalizable
        Example path: /api/some_canalizable/1/communication_channels/
        """
        canalizable = self.get_object()
        communication_channels = canalizable.communication_channels.all()
        serializer = CommunicationChannelSerializer(
            communication_channels, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @communication_channels.mapping.post
    def communication_channels_create(self, request, pk=None):
        """
        View for communication channel creation
        Example path: /api/some_canalizable/1/communication_channels/
        """
        canalizable = self.get_object()
        serializer = CommunicationChannelSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save(canalizable=canalizable)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=["get"],
        url_path="communication_channels/(?P<communication_channel_id>[^/.]+)",
    )
    def communication_channels_detail(
        self, request, pk=None, communication_channel_id=None
    ):
        """
        View for communication channel detail
        Example path: /api/some_canalizable/1/communication_channels/1/
        """
        canalizable = self.get_object()

        try:
            communication_channel = canalizable.communication_channels.get(
                pk=communication_channel_id
            )
        except ObjectDoesNotExist:
            return Response(
                {"detail": "Communication channel does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CommunicationChannelSerializer(
            communication_channel, context={"request": request}
        )

        return Response(serializer.data)

    @communication_channels_detail.mapping.put
    def communication_channels_update(
        self, request, pk=None, communication_channel_id=None
    ):
        """
        View for communication channel update
        Example path: /api/some_canalizable/1/communication_channels/1/
        """
        canalizable = self.get_object()

        try:
            communication_channel = canalizable.communication_channels.get(
                pk=communication_channel_id
            )
        except ObjectDoesNotExist:
            return Response(
                {"detail": "Communication channel does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CommunicationChannelSerializer(
            communication_channel,
            data=request.data,
            context={"request": request},
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @communication_channels_detail.mapping.delete
    def communication_channels_delete(
        self, request, pk=None, communication_channel_id=None
    ):
        """
        View for communication channel delete
        Example path: /api/some_canalizable/1/communication_channels/1/
        """
        canalizable = self.get_object()

        try:
            communication_channel = canalizable.communication_channels.get(
                pk=communication_channel_id
            )
        except ObjectDoesNotExist:
            return Response(
                {"detail": "Communication channel does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        communication_channel.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    def is_in_communication_channel_path(self, path):
        """
        Check if the current path is a view of BaseCommunicationChannelsViewSet
        """
        match = resolve(path)

        return "communication-channels" in match.view_name


class CommunicationChannelViewSet(viewsets.ModelViewSet):
    """
    CommunicationChannelViewSet class
    """

    queryset = models.CommunicationChannel.objects.all()
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    search_fields = ["id", "name", "message_id"]
    ordering_fields = ["id", "created", "modified", "name", "message_id"]
    serializer_class = CommunicationChannelSerializer
    permission_classes = [permissions.IsAuthenticated]

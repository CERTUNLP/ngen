# pylint: disable=broad-exception-caught

"""
Communication channel views
"""

import django_filters
from django.core.exceptions import ObjectDoesNotExist
from django.urls import resolve
from rest_framework import permissions, filters, status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ngen import models
from ngen.serializers.communication_channel import (
    CommunicationChannelSerializer,
    CommunicationChannelReducedSerializer,
)
from ngen.serializers.communication_type import CommunicationTypeSerializer
from ngen.permissions import CustomModelPermissions
from ngen.serializers.email_message import EmailMessageSerializer


class BaseCommunicationChannelsViewSet(viewsets.ModelViewSet):
    """
    Class that adds communication channel endpoints to channelable models
    e.g.:
    /api/case/1/communicationchannels/
    /api/case/1/communicationchannels/1
    /api/event/2/communicationchannels/3
    """

    permission_classes = [CustomModelPermissions]

    def get_serializer_class(self):
        """
        Get the serializer class.
        Use CommunicationChannelSerializer if the path corresponds to a communication channel view
        """
        if self.is_in_communication_channel_path(self.request.path):
            return CommunicationChannelSerializer

        return self.serializer_class

    @action(detail=True, methods=["get"], url_path="communicationchannels")
    def communication_channels(self, request, pk=None):
        """
        View for list of communication channels of a channelable
        Example path: /api/some_channelable/1/communicationchannels/
        """
        channelable = self.get_object()
        communication_channels = channelable.communication_channels.all().order_by("id")
        paginated_channels = self.paginator.paginate_queryset(
            communication_channels, request
        )
        serializer = CommunicationChannelReducedSerializer(
            paginated_channels, many=True, context={"request": request}
        )
        return self.paginator.get_paginated_response(serializer.data)

    @communication_channels.mapping.post
    def communication_channels_create(self, request, pk=None):
        """
        View for communication channel creation
        Example path: /api/some_channelable/1/communicationchannels/
        """
        channelable = self.get_object()
        serializer = CommunicationChannelSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save(channelable=channelable)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=["get"],
        url_path="communicationchannels/(?P<communication_channel_id>[^/.]+)",
    )
    def communication_channels_detail(
        self, request, pk=None, communication_channel_id=None
    ):
        """
        View for communication channel detail
        Example path: /api/some_channelable/1/communicationchannels/1/
        """
        channelable = self.get_object()

        try:
            communication_channel = channelable.communication_channels.get(
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
        Example path: /api/some_channelable/1/communicationchannels/1/
        """
        channelable = self.get_object()

        try:
            communication_channel = channelable.communication_channels.get(
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
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @communication_channels_detail.mapping.patch
    def communication_channels_partial_update(
        self, request, pk=None, communication_channel_id=None
    ):
        """
        View for communication channel update
        Example path: /api/some_channelable/1/communicationchannels/1/
        """
        channelable = self.get_object()

        try:
            communication_channel = channelable.communication_channels.get(
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
        Example path: /api/some_channelable/1/communicationchannels/1/
        """
        channelable = self.get_object()

        try:
            communication_channel = channelable.communication_channels.get(
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

    queryset = models.CommunicationChannel.objects.all().order_by("id")
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    search_fields = ["id", "name", "message_id"]
    ordering_fields = ["id", "created", "modified", "name", "message_id"]
    serializer_class = CommunicationChannelSerializer
    permission_classes = [CustomModelPermissions]

    serializer_class_by_action = {
        "list": CommunicationChannelReducedSerializer,
    }

    def get_serializer_class(self):
        """
        Use reduced serializer for list action, complete serializer for other actions
        """
        return self.serializer_class_by_action.get(self.action, self.serializer_class)

    @action(detail=True, methods=["post"], url_path="communicate")
    def communicate(self, request, pk=None):
        """
        Endpoint to send an email in a communication channel.
        """

        try:
            validation = self.validate_params(request)
            if not validation["success"]:
                return Response(
                    {"error": ", ".join(validation["errors"])},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            params = self.build_params(request)
            channel = self.get_object()
            sent_email = channel.communicate(**params)
            data = EmailMessageSerializer(sent_email, context={"request": request}).data
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def validate_params(self, request):
        """
        Validates the parameters for the communicate action
        """
        result = {"success": True, "errors": []}
        subject = request.data.get("subject")
        body = request.data.get("body")
        template = request.data.get("template")

        if not body:
            result["success"] = False
            result["errors"].append("Body is required")
        elif not isinstance(body, str):
            result["success"] = False
            result["errors"].append("Body must be a string")

        if subject and not isinstance(subject, str):
            result["success"] = False
            result["errors"].append("Subject must be a string")

        if template and not isinstance(template, str):
            result["success"] = False
            result["errors"].append("Template must be a string")

        return result

    def build_params(self, request):
        """
        Builds the parameters for the communicate endpoint
        """
        subject = request.data.get("subject")
        body = request.data.get("body")
        template = request.data.get("template")
        template_params = request.data.get("template_params")

        return {
            "subject": subject,
            "body": body,
            "template": template,
            "template_params": template_params,
        }


class CommunicationTypeViewSet(viewsets.ModelViewSet):
    """
    CommunicationTypeViewSet class
    """

    queryset = models.CommunicationType.objects.all().order_by("id")
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    search_fields = ["type"]
    ordering_fields = ["id", "created", "modified", "type"]
    serializer_class = CommunicationTypeSerializer
    permission_classes = [CustomModelPermissions]

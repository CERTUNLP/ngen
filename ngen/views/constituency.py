from django.shortcuts import get_object_or_404
import django_filters
from django.db.models import Count
from rest_framework import filters, viewsets, mixins
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response

from ngen import models, serializers
from rest_framework import permissions, status, viewsets
from ngen.filters import NetworkFilter, ContactFilter, NetworkEntityFilter
from ngen.models.constituency import ContactCheck
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from ngen.tasks import send_contact_checks
from ngen.permissions import (
    CustomApiViewPermission,
    CustomMethodApiViewPermission,
    CustomModelPermissions,
)


class NetworkViewSet(viewsets.ModelViewSet):
    queryset = models.Network.objects.annotate(
        contact_count=Count("contacts"), children_count=Count("children")
    )
    serializer_class = serializers.NetworkSerializer
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    search_fields = [
        "cidr",
        "type",
        "domain",
        "contacts__username",
        "network_entity__name",
    ]
    filterset_class = NetworkFilter
    ordering_fields = [
        "id",
        "created",
        "modified",
        "cidr",
        "domain",
        "type",
        "active",
        "address_value",
        "network_entity",
        "network_entity__name",
        "contact_count",
        "contacts__username",
        "children_count",
    ]
    permission_classes = [CustomModelPermissions]


class NetworkAdminNetworkViewSet(NetworkViewSet):
    serializer_class = serializers.NetworkAdminNetworkSerializer
    permission_classes = [CustomMethodApiViewPermission]
    required_permissions = {
        "GET": ["ngen.view_network_network_admin"],
        "HEAD": ["ngen.view_network_network_admin"],
        "POST": ["ngen.add_network_network_admin"],
        "PUT": ["ngen.change_network_network_admin"],
        "PATCH": ["ngen.change_network_network_admin"],
        "DELETE": ["ngen.delete_network_network_admin"],
    }

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        return queryset.filter(contacts__user=user).distinct()


class NetworkEntityViewSet(viewsets.ModelViewSet):
    queryset = models.NetworkEntity.objects.annotate(
        networks_count=Count("networks")
    ).order_by("id")
    serializer_class = serializers.NetworkEntitySerializer
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    search_fields = ["name", "slug"]
    filterset_class = NetworkEntityFilter
    ordering_fields = ["id", "created", "modified", "name", "slug", "networks_count"]
    permission_classes = [CustomModelPermissions]


class NetworkAdminNetworkEntityViewSet(NetworkEntityViewSet):
    serializer_class = serializers.NetworkAdminNetworkEntitySerializer
    permission_classes = [CustomMethodApiViewPermission]
    required_permissions = {
        "GET": ["ngen.view_networkentity_network_admin"],
        "HEAD": ["ngen.view_networkentity_network_admin"],
        "POST": ["ngen.add_networkentity_network_admin"],
        "PUT": ["ngen.change_networkentity_network_admin"],
        "PATCH": ["ngen.change_networkentity_network_admin"],
        "DELETE": ["ngen.delete_networkentity_network_admin"],
    }

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        return queryset.filter(networks__contacts__user=user).distinct()


class ContactViewSet(viewsets.ModelViewSet):
    queryset = models.Contact.objects.all()
    serializer_class = serializers.ContactSerializer
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    search_fields = [
        "name",
        "username",
        "role",
        "type",
        "priority",
    ]
    filterset_class = ContactFilter
    ordering_fields = [
        "id",
        "created",
        "modified",
        "name",
        "username",
        "role",
        "priority",
        "type",
        "last_check",
        "last_check__confirmed",
    ]
    permission_classes = [CustomModelPermissions]


class NetworkAdminContactViewSet(ContactViewSet):
    serializer_class = serializers.NetworkAdminContactSerializer
    permission_classes = [CustomMethodApiViewPermission]
    required_permissions = {
        "GET": ["ngen.view_contact_network_admin"],
        "HEAD": ["ngen.view_contact_network_admin"],
        "POST": ["ngen.add_contact_network_admin"],
        "PUT": ["ngen.change_contact_network_admin"],
        "PATCH": ["ngen.change_contact_network_admin"],
        "DELETE": ["ngen.delete_contact_network_admin"],
    }

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        # user is contact.user or networks are in networks__contacts for user
        return queryset.filter(
            models.Q(user=user) | models.Q(networks__contacts__user=user)
        ).distinct()


class EntityMinifiedViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = models.NetworkEntity.objects.all()
    serializer_class = serializers.EntityMinifiedSerializer
    pagination_class = None
    permission_classes = [CustomApiViewPermission]
    required_permissions = ["ngen.view_minified_entity"]


class ContactMinifiedViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = models.Contact.objects.all()
    serializer_class = serializers.ContactMinifiedSerializer
    pagination_class = None
    permission_classes = [CustomApiViewPermission]
    required_permissions = ["ngen.view_minified_contact"]


## agregar que se pueda ejecutar un contact check desde el admin manualmente para un contacto
class ContactCheckViewSet(viewsets.ModelViewSet):
    queryset = models.ContactCheck.objects.all()
    serializer_class = serializers.ContactCheckSerializer
    permission_classes = [CustomModelPermissions]
    filter_backends = [
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    search_fields = ["contact__name", "contact__username", "uuid", "notes"]
    filterset_fields = ["confirmed", "contact", "accessed_at"]
    ordering_fields = ["id", "created", "accessed_at", "confirmed", "contact"]

    @action(
        detail=False,
        methods=["post"],
        url_path=r"contact/(?P<contact_id>\d+)/send",
        permission_classes=[CustomModelPermissions],
    )
    def send(self, request, contact_id=None):
        """
        Trigger sending a contact check email/task for a given contact_id.
        Returns the URL for the created contact check.
        """
        contact_check = models.ContactCheck.objects.create(contact_id=contact_id)
        # Use serializer to get the URL if defined, or build it manually
        serializer = self.get_serializer(contact_check)
        url = serializer.data.get("url")
        return Response(
            {
                "detail": "Contact check email sent.",
                "uuid": contact_check.uuid,
                "url": url,
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["get"],
        url_path=r"contact/(?P<contact_id>\d+)",
        permission_classes=[CustomModelPermissions],
    )
    def get_by_contact_id(self, request, contact_id=None):
        """
        Get last contact check(s) for a given contact_id.
        """
        contact_checks = models.ContactCheck.objects.filter(
            contact_id=contact_id
        ).order_by("-created")
        serializer = self.get_serializer(contact_checks, many=True)
        print(
            f"Contact checks for contact_id {contact_id}: {serializer.data} {len(contact_checks)}"
        )
        return Response(serializer.data[:1], status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["post"],
        url_path=r"resend/(?P<uuid>[0-9a-f-]+)",
        permission_classes=[CustomModelPermissions],
    )
    def resend(self, request, uuid=None):
        """
        Create new contact check for a contact related to the given uuid contact check.
        Returns the URL for the created contact check.
        """
        contact_check = get_object_or_404(models.ContactCheck, uuid=uuid)
        new_check = models.ContactCheck.objects.create(contact=contact_check.contact)
        serializer = self.get_serializer(new_check)
        url = serializer.data.get("url")
        return Response(
            {
                "detail": "Contact check email resent.",
                "uuid": new_check.uuid,
                "url": url,
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["post"],
        url_path=r"confirm/(?P<uuid>[0-9a-f-]+)",
        permission_classes=[CustomModelPermissions],
    )
    def confirm(self, request, uuid=None):
        """
        Mark a contact check as confirmed or rejected.
        """
        check = get_object_or_404(models.ContactCheck, uuid=uuid)
        check.confirmed = True
        check.save()
        serializer = self.get_serializer(check)

        return Response(
            {
                "detail": "Contact check status updated successfully.",
                "uuid": check.uuid,
                "url": serializer.data.get("url"),
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["get", "post"],
        url_path=r"validate/(?P<uuid>[0-9a-f-]+)",
        permission_classes=[permissions.AllowAny],
    )
    def validate(self, request, uuid=None):
        check = get_object_or_404(ContactCheck, uuid=uuid)

        if check.accessed_at:
            return Response(
                {"detail": "This link has already been used."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not check.is_valid:
            return Response(
                {"detail": "This contact check is no longer valid."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.method == "GET":
            confirm = request.query_params.get("confirm")
            if confirm == "true":
                check.accessed_at = timezone.now()
                check.confirmed = True
                check.save()
                return Response(
                    {"detail": "Verification confirmed successfully."},
                    status=status.HTTP_200_OK,
                )
            return Response(
                {
                    "contact": {
                        "name": check.contact.name,
                        "username": check.contact.username,
                    },
                    "confirmed": None,
                    "notes": "",
                },
                status=status.HTTP_200_OK,
            )

        if request.method == "POST":
            serializer = serializers.constituency.ContactCheckValidationSerializer(
                data=request.data
            )
            serializer.is_valid(raise_exception=True)

            check.accessed_at = timezone.now()
            check.confirmed = serializer.validated_data["confirmed"]
            check.notes = serializer.validated_data.get("notes")
            check.save()
            return Response({"detail": "Verification registered successfully."})

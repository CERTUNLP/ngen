import jwt
from django.conf import settings
from rest_framework import authentication, exceptions
from rest_framework import filters

from ngen.models import User


class MergedModelFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if not view.detail:
            return queryset.filter(parent__isnull=True)
        return queryset

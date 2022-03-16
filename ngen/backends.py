from rest_framework import filters


class EventRootFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if not view.detail:
            return queryset.filter(parent__isnull=True)
        return queryset

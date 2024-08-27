from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from ngen.models import *


class NetworkAdmin(admin.ModelAdmin):
    readonly_fields = ["parent"]


class EventAdmin(admin.ModelAdmin):
    readonly_fields = ["parent"]

    def save_model(self, request, obj, form, change):
        if not obj.reporter:
            obj.reporter = request.user
        super().save_model(request, obj, form, change)


# administration
admin.site.register(Feed)
admin.site.register(Priority)
admin.site.register(Tlp)
admin.site.register(User, UserAdmin)

# announcement
admin.site.register(Announcement)

# artifact
admin.site.register(Artifact)
admin.site.register(ArtifactRelation)
admin.site.register(ArtifactEnrichment)

# case
admin.site.register(Case)
admin.site.register(Event, EventAdmin)
admin.site.register(Evidence)
admin.site.register(CaseTemplate)

# constituency
admin.site.register(Network, NetworkAdmin)
admin.site.register(Contact)
admin.site.register(NetworkEntity)

# message
admin.site.register(Message)

# state
admin.site.register(State)
admin.site.register(Edge)

# taxonomy
admin.site.register(TaxonomyGroup)
admin.site.register(Taxonomy)
admin.site.register(Report)
admin.site.register(Playbook)
admin.site.register(Task)
admin.site.register(TodoTask)

# communication
admin.site.register(CommunicationChannel)
admin.site.register(CommunicationType)
admin.site.register(CommunicationChannelTypeRelation)

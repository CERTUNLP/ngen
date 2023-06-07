from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from ngen.models import User
from ngen.models import *

# administration
admin.site.register(Feed)
admin.site.register(Priority)
admin.site.register(Tlp)
admin.site.register(User, UserAdmin)

# announcement
admin.site.register(Announcement)

# artifact
# admin.site.register(Artifact)
admin.site.register(ArtifactRelation)
# admin.site.register(ArtifactRelated)
admin.site.register(ArtifactEnrichment)

# case
admin.site.register(Case)
admin.site.register(Event)
admin.site.register(Evidence)
admin.site.register(CaseTemplate)
admin.site.register(ActiveSession)

# constituency
# admin.site.register(NetworkManager)

class NetworkAdmin(admin.ModelAdmin):
    readonly_fields = ['parent']

admin.site.register(Network, NetworkAdmin)
admin.site.register(Contact)
admin.site.register(NetworkEntity)

# message
admin.site.register(Message)

# state
admin.site.register(State)
admin.site.register(Edge)

# taxonomy
admin.site.register(Taxonomy)
admin.site.register(Report)
admin.site.register(Playbook)
admin.site.register(Task)
admin.site.register(TodoTask)

# utils
# admin.site.register(NgenModel)
# admin.site.register(NgenTreeModel)
# admin.site.register(NgenMergeableModel)
# admin.site.register(NgenEvidenceMixin)
# admin.site.register(NgenPriorityMixin)
# admin.site.register(AddressManager)
# admin.site.register(NgenAddressModel)

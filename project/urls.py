"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

import comment.api.views as comment_views
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.authtoken import views as authtokenviews
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from ngen import views
from project import settings

router = DefaultRouter()
router.register(r"administration/tlp", views.TlpViewSet)
router.register(r"administration/feed", views.FeedViewSet)
router.register(r"administration/priority", views.PriorityViewSet)
router.register(r"state", views.StateViewSet, basename="state")
router.register(r"edge", views.EdgeViewSet, basename="edge")
router.register(r"template", views.CaseTemplateViewSet, basename="casetemplate")
router.register(r"case", views.CaseViewSet, basename="case")
router.register(
    r"communicationchannel",
    views.CommunicationChannelViewSet,
    basename="communicationchannel",
)
router.register(
    r"communication_type", views.CommunicationTypeViewSet, basename="communicationtype"
)
router.register(r"emailmessage", views.EmailMessageViewSet, basename="emailmessage")
router.register(r"evidence", views.EvidenceViewSet, basename="evidence")
router.register(r"event", views.EventViewSet, basename="event")
router.register(r"solvedmark", views.SolvedMarkViewSet, basename="solvedmark")
router.register(r"taxonomy", views.TaxonomyViewSet, basename="taxonomy")
router.register(r"taxonomygroup", views.TaxonomyGroupViewSet, basename="taxonomygroup")
router.register(r"report", views.ReportViewSet, basename="report")
router.register(r"network", views.NetworkViewSet, basename="network")
router.register(r"contact", views.ContactViewSet, basename="contact")
router.register(r"entity", views.NetworkEntityViewSet, basename="networkentity")
router.register(r"user", views.UserViewSet, basename="user")
router.register(r"profile", views.UserProfileViewSet, basename="profile")
router.register(r"playbook", views.PlaybookViewSet, basename="playbook")
router.register(r"task", views.TaskViewSet, basename="task")
router.register(r"todo", views.TodoTaskViewSet, basename="todo")
router.register(r"artifact", views.ArtifactViewSet, basename="artifact")
router.register(
    r"artifactenrichment",
    views.ArtifactEnrichmentViewSet,
    basename="artifactenrichment",
)
router.register(
    r"artifactrelation", views.ArtifactRelationViewSet, basename="artifactrelation"
)
router.register(r"audit", views.AuditViewSet, basename="logentry")
router.register(r"announcement", views.AnnouncementViewSet, basename="announcement")
router.register(r"constance", views.ConstanceViewSet, basename="constance")
router.register(
    r"stringidentifier", views.StringIdentifierViewSet, basename="stringidentifier"
)
# router.register(r"comments", views.CommentViewSet)
router.register(r"register", views.RegisterViewSet, basename="register")
router.register(r"groups", views.GroupViewSet, basename="group")
router.register(r"permission", views.PermissionViewSet, basename="permission")
router.register(r"contenttype", views.ContentTypeViewSet, basename="contenttype")
router.register(
    r"networkadmin/event", views.NetworkAdminEventViewSet, basename="networkadminevent"
)
router.register(
    r"networkadmin/case", views.NetworkAdminCaseViewSet, basename="networkadmincase"
)
router.register(
    r"networkadmin/evidence",
    views.NetworkAdminEvidenceViewSet,
    basename="networkadminevidence",
)
router.register(
    r"networkadmin/network",
    views.NetworkAdminNetworkViewSet,
    basename="networkadminnetwork",
)
router.register(
    r"networkadmin/networkentity",
    views.NetworkAdminNetworkEntityViewSet,
    basename="networkadminnetworkentity",
)
router.register(
    r"networkadmin/contact",
    views.NetworkAdminContactViewSet,
    basename="networkadmincontact",
)
# router.register(r"login", views.LoginViewSet, basename="login")
router.register(
    r"minified/taxonomy", views.TaxonomyMinifiedViewSet, basename="minified-taxonomy"
)
router.register(
    r"minified/taxonomygroup",
    views.TaxonomyGroupMinifiedViewSet,
    basename="minified-taxonomygroup",
)
router.register(r"minified/tlp", views.TlpMinifiedViewSet, basename="minified-tlp")
router.register(r"minified/feed", views.FeedMinifiedViewSet, basename="minified-feed")
router.register(
    r"minified/priority", views.PriorityMinifiedViewSet, basename="minified-priority"
)
router.register(
    r"minified/state", views.StateMinifiedViewSet, basename="minified-state"
)
router.register(
    r"minified/entity", views.EntityMinifiedViewSet, basename="minified-entity"
)
router.register(
    r"minified/contact", views.ContactMinifiedViewSet, basename="minified-contact"
)
router.register(r"minified/user", views.UserMinifiedViewSet, basename="minified-user")
router.register(
    r"minified/permission",
    views.PermissionMinifiedViewSet,
    basename="minified-permission",
)
router.register(
    r"minified/group", views.GroupMinifiedViewSet, basename="minified-group"
)
router.register(r"minified/case", views.CaseMinifiedViewSet, basename="minified-case")
router.register(
    r"minified/artifact", views.ArtifactMinifiedViewSet, basename="minified-artifact"
)
router.register(r"minified/tag", views.TagMinifiedViewSet, basename="minified-tag")
router.register(r"ngenconfig", views.SettingsViewSet, basename="settings")
router.register(r"tag", views.TagViewSet, basename="tag")

router.register(r"eventanalysis", views.EventAnalysisViewSet, basename="eventanalysis")

router.register(
    r"analyzermapping", views.AnalyzerMappingViewSet, basename="analyzermapping"
)

if settings.ELASTIC_ENABLED:
    from ngen.documents import CaseDocumentViewSet

    router.register(r"search/case", CaseDocumentViewSet, basename="casedocument")

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("api/admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/comment/", comment_views.CommentList.as_view(), name="comment-list"),
    path(
        "api/comment/create/",
        comment_views.CommentCreate.as_view(),
        name="comment-create",
    ),
    path(
        "api/comment/<int:pk>/",
        comment_views.CommentDetail.as_view(),
        name="comment-detail",
    ),
    path(
        "api/user/<int:pk>/audit/",
        views.tools.UserAuditsListView.as_view({"get": "list"}),
        name="user-logentry-list",
    ),
    path("api/token/", views.CustomTokenObtainPairView.as_view(), name="token-create"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token-verify"),
    path("api/token/simple/", authtokenviews.obtain_auth_token, name="token-simple"),
    path("api/", include("rest_framework.urls", namespace="rest_framework")),
    path("api/logout/", views.LogoutView.as_view(), name="logout"),
    path(
        "api/ctoken/", views.CookieTokenObtainPairView.as_view(), name="ctoken-create"
    ),
    path(
        "api/ctoken/refresh/",
        views.CookieTokenRefreshView.as_view(),
        name="ctoken-refresh",
    ),
    path(
        "api/ctoken/logout/",
        views.CookieTokenLogoutView.as_view(),
        name="ctoken-logout",
    ),
    path("__debug__/", include("debug_toolbar.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    path(
        "api/dashboard/events",
        views.dashboards.events.DashboardEventsView.as_view(),
        name="dashboard-events",
    ),
    path(
        "api/dashboard/cases",
        views.dashboards.cases.DashboardCasesView.as_view(),
        name="dashboard-cases",
    ),
    path(
        "api/dashboard/feeds",
        views.dashboards.feeds.DashboardFeedsView.as_view(),
        name="dashboard-feeds",
    ),
    path(
        "api/dashboard/network_entities",
        views.dashboards.network_entities.DashboardNetworkEntitiesView.as_view(),
        name="dashboard-network-entities",
    ),
    path(
        "api/constance/upload/team_logo",
        views.TeamLogoFileUploadView.as_view(),
    ),
    path(
        "api/lookup/<str:ip_or_domain>/",
        views.WhoisLookupView.as_view(),
        name="whois_lookup",
    ),
    path(
        "api/result/<str:task_id>/", views.TaskStatusView.as_view(), name="task_status"
    ),
    path(
        "api/version/",
        views.VersionView.as_view(),
        name="version",
    ),
]

if not settings.ELASTIC_ENABLED:
    urlpatterns += [
        re_path(r"^api/search", views.DisabledView.as_view(), name="disabled_view")
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

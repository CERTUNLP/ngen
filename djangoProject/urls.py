"""djangoProject URL Configuration

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
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from djangoProject import settings
from ngen import views
from ngen.documents import CaseDocumentViewSet

router = DefaultRouter()
router.register(r'administration/tlp', views.TlpViewSet)
router.register(r'administration/feed', views.FeedViewSet)
router.register(r'administration/priority', views.PriorityViewSet)
router.register(r'state', views.StateViewSet)
router.register(r'edge', views.EdgeViewSet)
router.register(r'template', views.CaseTemplateViewSet)
router.register(r'case', views.CaseViewSet)
router.register(r'evidence', views.EvidenceViewSet)
router.register(r'event', views.EventViewSet)
router.register(r'taxonomy', views.TaxonomyViewSet)
router.register(r'report', views.ReportViewSet)
router.register(r'network', views.NetworkViewSet)
router.register(r'contact', views.ContactViewSet)
router.register(r'entity', views.NetworkEntityViewSet)
router.register(r'user', views.UserViewSet)
router.register(r'playbook', views.PlaybookViewSet)
router.register(r'task', views.TaskViewSet)
router.register(r'todo', views.TodoTaskViewSet)
router.register(r'artifact', views.ArtifactViewSet)
router.register(r"announcement", views.AnnouncementViewSet)
# router.register(r"comments", views.CommentViewSet)
router.register(r"register", views.RegisterViewSet, basename="register")
router.register(r"checkSession", views.ActiveSessionViewSet, basename="check-session")
router.register(r"login", views.LoginViewSet, basename="login")
router.register(r"logout", views.LogoutViewSet, basename="logout")
router.register(r'search/case',
                CaseDocumentViewSet,
                basename='casedocument')
# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/comments/', comment_views.CommentList.as_view(), name='comment-list'),
    path('api/comments/create/', comment_views.CommentCreate.as_view(), name='comment-create'),
    path('api/comments/<int:pk>/', comment_views.CommentDetail.as_view(), name='comment-detail'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('about/', views.AboutView.as_view()),
    path('__debug__/', include('debug_toolbar.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

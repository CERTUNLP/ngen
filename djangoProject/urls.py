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
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from djangoProject import settings
from ngen import views

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

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('about/', views.AboutView.as_view()),
    path('__debug__/', include('debug_toolbar.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

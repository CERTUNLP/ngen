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
from django.contrib import admin
from django.urls import include, path
from rest_framework_extensions.routers import ExtendedDefaultRouter

from ngen import views
from ngen.views import AboutView

router = ExtendedDefaultRouter()
router.register(r'administration/tlp', views.TlpViewSet)
router.register(r'administration/feed', views.FeedViewSet)
router.register(r'administration/priority', views.PriorityViewSet)
router.register(r'case', views.CaseViewSet, basename='case').register(r'events',
                                                                      views.EventViewSet,
                                                                      basename='case-events',
                                                                      parents_query_lookups=['case'])
router.register(r'state', views.StateViewSet)
router.register(r'behavior', views.BehaviorViewSet)
router.register(r'edge', views.EdgeViewSet)
router.register(r'template', views.CaseTemplateViewSet)
router.register(r'event', views.EventViewSet)
router.register(r'taxonomy', views.TaxonomyViewSet)
router.register(r'report', views.ReportViewSet)
router.register(r'network', views.NetworkViewSet)
router.register(r'contact', views.ContactViewSet)
router.register(r'entity', views.NetworkEntityViewSet)
router.register(r'user', views.UserViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('about/', AboutView.as_view()),

]

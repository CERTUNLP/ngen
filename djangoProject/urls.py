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
from rest_framework import routers

from ngen import views

router = routers.DefaultRouter()
router.register(r'incidents', views.IncidentViewSet)
router.register(r'incident/types', views.IncidentTypeViewSet)
router.register(r'incident/type/taxonomy/value', views.TaxonomyValueViewSet)
router.register(r'incident/type/taxonomy/predicate', views.TaxonomyPredicateViewSet)
router.register(r'incident/feeds', views.IncidentFeedViewSet)
router.register(r'incident/states', views.IncidentStateViewSet)
router.register(r'incident/state/behavior', views.StateBehaviorViewSet)
router.register(r'incident/tlps', views.IncidentTlpViewSet)
router.register(r'incident/priorities', views.IncidentPriorityViewSet)
router.register(r'incident/priority/impact', views.IncidentImpactViewSet)
router.register(r'incident/priority/urgency', views.IncidentUrgencyViewSet)
router.register(r'networks', views.NetworkViewSet)
router.register(r'network/admins', views.NetworkAdminViewSet)
router.register(r'network/entities', views.NetworkEntityViewSet)
router.register(r'network/hosts', views.HostViewSet)
router.register(r'users', views.UserViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]

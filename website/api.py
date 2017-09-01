from django.conf.urls import url, include
from rest_framework import routers

from observation.api import ObservationViewSet
from observation.api import GroupViewSet
from observation.api import FamilyViewSet
from observation.api import SpeciesViewSet
from observation.api import CoordinatesViewSet


router = routers.DefaultRouter()

router.register(r'observations', ObservationViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'family', FamilyViewSet)
router.register(r'species', SpeciesViewSet)
router.register(r'coordinates', CoordinatesViewSet)


urlpatterns = [
    url(r'', include(router.urls)),
]
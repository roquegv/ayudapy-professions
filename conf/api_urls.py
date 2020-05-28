from rest_framework import routers
from core import api as core_api
from org import api as org_api
from ollas import api as ollas_api
from oficios import api as oficios_api
from django.urls import include, path

PREFIX = "api/v1"

router = routers.DefaultRouter()
# CORE
router.register(r'helprequests', core_api.HelpRequestViewSet, 'helprequests')
router.register(r'helprequestsgeo', core_api.HelpRequestGeoViewSet)
router.register(r'devices', core_api.DeviceViewSet)
router.register(r'cities', core_api.CitiesViewSet)
# ORG
router.register(r'donationcenters', org_api.DonationCenterViewSet)
router.register(r'donationcentersgeo', org_api.DonationCenterGeoViewSet)
# Ollas Populares
router.register(r'ollaspopulares', ollas_api.OllaPopularViewSet, 'ollaspopulares')
router.register(r'ollaspopularesgeo', ollas_api.OllaPopularGeoViewSet)
# Oficios
router.register(r'oficios', oficios_api.OficioViewSet, 'oficios')
router.register(r'oficiosgeo', oficios_api.OficioGeoViewSet)

urlpatterns = [
    path(f"{PREFIX}/", include(router.urls)),
    path(f"{PREFIX}/stats", core_api.StatsView)
]


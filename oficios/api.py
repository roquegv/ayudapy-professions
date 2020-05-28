from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from rest_framework_gis.filters import InBBoxFilter

from core.middleware import USER_TYPE_DEVICE
from core.serializers import DeviceSerializer
from core.models import Device, User

from oficios.models import Oficio
from oficios.serializers import OficioSerializer, OficioGeoJSONSerializer

"""
    API endpoints that allows search queries on Oficio 0
"""


# SEARCH OFICIOS
class DynamicSearchFilter(filters.SearchFilter):
    def get_search_fields(self, view, request):
        return request.GET.getlist('search_fields', [])


class OficioViewSet(viewsets.ModelViewSet):
    queryset = Oficio.objects.filter(active=True, resolved=False).order_by('-id')
    serializer_class = OficioSerializer
    filter_backends = [InBBoxFilter, DjangoFilterBackend, DynamicSearchFilter, ]
    search_fields = ['title', 'phone',]
    filterset_fields = {
            'added': ['gte', 'lte'],
            'city': ['exact'],
    }
    bbox_filter_field = 'location'
    bbox_filter_include_overlapping = True


class OficioGeoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Oficio.objects.filter(active=True, resolved=False).order_by('-pk')
    pagination_class = None
    serializer_class = OficioGeoJSONSerializer
    bbox_filter_field = 'location'
    filter_backends = (InBBoxFilter, DynamicSearchFilter,)
    bbox_filter_include_overlapping = True

from django_filters import FilterSet, Filter, BaseInFilter
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

class OficioFilter(FilterSet):
    categories = BaseInFilter(field_name="categories", lookup_expr='in')
    added_gte = Filter(field_name="added", lookup_expr='gte')
    added_lte = Filter(field_name="added", lookup_expr='lte')
    city = Filter(field_name="city", lookup_expr='exact')
    class Meta:
        model = Oficio
        fields = ["categories", "added_gte", "added_lte", "city"]

class OficioViewSet(viewsets.ModelViewSet):
    queryset = Oficio.objects.filter(active=True, resolved=False).order_by('-id')
    serializer_class = OficioSerializer
    filter_backends = [InBBoxFilter, DjangoFilterBackend, DynamicSearchFilter, ]
    search_fields = ['title', 'phone',]
    # filterset_fields = {
    #         'added': ['gte', 'lte'],
    #         'categories': ['in'],
    #         'city': ['exact'],
    #         'categories': ['exact'],
    # }
    filterset_class = OficioFilter
    # filter_fields = ('categories')
    bbox_filter_field = 'location'
    bbox_filter_include_overlapping = True


class OficioGeoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Oficio.objects.filter(active=True, resolved=False).order_by('-pk')
    pagination_class = None
    serializer_class = OficioGeoJSONSerializer
    bbox_filter_field = 'location'
    filter_backends = (InBBoxFilter, DynamicSearchFilter,)
    bbox_filter_include_overlapping = True

    def get_queryset(self):
        queryset = Oficio.objects.all()
        filter_value = self.request.query_params.get('categories', None)
        if filter_value is not None:
            queryset = queryset.filter(categories__in=filter_value.split(","))
        return queryset

from datetime import date, timedelta
from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from rest_framework_gis.filters import InBBoxFilter

from core.middleware import USER_TYPE_DEVICE
from core.models import HelpRequest, Device, User
from core.serializers import HelpRequestSerializer, HelpRequestGeoJSONSerializer, DeviceSerializer, CitiesSerializer

"""
    API endpoints that allows search queries on HelpRequest 0
"""


# SEARCH HELP REQUESTS
class DynamicSearchFilter(filters.SearchFilter):
    def get_search_fields(self, view, request):
        return request.GET.getlist('search_fields', [])


class HelpRequestViewSet(viewsets.ModelViewSet):
    queryset = HelpRequest.objects.filter(active=True, resolved=False).order_by('-id')
    serializer_class = HelpRequestSerializer
    filter_backends = [InBBoxFilter, DjangoFilterBackend, DynamicSearchFilter, ]
    search_fields = ['title', 'phone',]
    filterset_fields = {
            'added': ['gte', 'lte', 'date'],
            'city': ['exact'],
    }
    bbox_filter_field = 'location'
    bbox_filter_include_overlapping = True


class HelpRequestGeoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = HelpRequest.objects.filter(active=True, resolved=False).order_by('-pk')
    pagination_class = None
    serializer_class = HelpRequestGeoJSONSerializer
    bbox_filter_field = 'location'
    filter_backends = (InBBoxFilter, DynamicSearchFilter,)
    bbox_filter_include_overlapping = True


class CitiesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = HelpRequest.objects.all().values('city', 'city_code').distinct().order_by('city_code')
    pagination_class = None
    serializer_class = CitiesSerializer


def StatsView(request):
    today = date.today()
    stats = dict(
        total_active=HelpRequest.objects.filter(active=True, resolved=False).count(),
        total_active_unique_phone=HelpRequest.objects.filter(active=True, resolved=False).distinct('phone').count(),
        total_resolved=HelpRequest.objects.filter(resolved=True).count(),
        today=HelpRequest.objects.filter(added__date=today, active=True).count(),
        yesterday=HelpRequest.objects.filter(added__date=today - timedelta(days=1), active=True).count(),
    )
    return JsonResponse(stats, )


"""
API to create/update/remove devices.
Will be used by the Mobile Client
"""


class DeviceViewSet(mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):

    serializer_class = DeviceSerializer
    queryset = Device.objects.all()
    lookup_field = "device_id"

    """
    Create a model instance.
    """
    def create(self, request, *args, **kwargs):

        # create device
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # create user/device
        u = User()
        u.created_ip_address = request.META.get('REMOTE_ADDR')
        u.user_type = USER_TYPE_DEVICE
        u.user_value = serializer.data['device_id']
        u.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}



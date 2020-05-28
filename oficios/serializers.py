from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer, GeoModelSerializer

from oficios.models import Oficio


class OficioSerializer(GeoModelSerializer):
    class Meta:
        model = Oficio
        fields = ['id', 'title', 'message', 'name', 'phone', 'address', 'city', 'location', 'picture', 'active', 'added']
        geo_field = 'location'


class OficioGeoJSONSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Oficio
        fields = ['pk', 'title','name', 'added']
        geo_field = 'location'

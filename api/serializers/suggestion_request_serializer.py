from rest_framework import serializers
from rest_framework_gis import serializers as geo_serializers
from django.core.exceptions import ObjectDoesNotExist

from api.models.sport import Sport


class SuggestionRequestSerializer(serializers.Serializer):
    def validate(self, attrs):
        if 'sport' in attrs:
            try:
                Sport.objects.get(id=attrs['sport'])
            except ObjectDoesNotExist:
                raise serializers.ValidationError('invalid sport')

        return attrs

    sport = serializers.IntegerField(required=False)

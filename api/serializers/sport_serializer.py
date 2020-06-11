from api.models.sport import Sport 
from rest_framework import serializers


class SportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sport
        fields = '__all__'
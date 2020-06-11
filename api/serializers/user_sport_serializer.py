from api.models.user_sport import UserSport
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator


class UserSportSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSport
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=UserSport.objects.all(),
                fields=['user', 'sport']
            )
        ]

from django.utils import timezone
from rest_framework import serializers

from api.models.constants import ACCEPTED
from api.models.participation_request import ParticipationRequest
from api.models.user import User
from api.models.workout import Workout
from .user_serializer import MinimalUserSerializer


class BasicWorkoutInputSerializer(serializers.ModelSerializer):
    signed_people = serializers.SerializerMethodField()

    def get_signed_people(self, obj):
        return get_people_signed_for_a_workout(obj.id)

    @staticmethod
    def validate_less_than(smaller_key, greater_key, attrs, error_message):
        if smaller_key in attrs and greater_key in attrs and attrs[smaller_key] > attrs[greater_key]:
            raise serializers.ValidationError(error_message)

    def validate(self, attrs):
        FullWorkoutSerializer.validate_less_than('start_time', 'end_time', attrs, 'end_before_start')
        FullWorkoutSerializer.validate_less_than('age_min', 'age_max', attrs, 'age_min_gt_age_max')

        if 'start_time' in attrs and attrs['start_time'] < timezone.now():
            raise serializers.ValidationError('start_time_before_now')

        return attrs

    class Meta:
        model = Workout
        fields = '__all__'


class BasicWorkoutOutputSerializer(BasicWorkoutInputSerializer):
    user = MinimalUserSerializer()


def get_people_signed_for_a_workout(workout):
    return 1 + ParticipationRequest.objects.filter(workout=workout, status=ACCEPTED).count()


class MinimalWorkoutSerializer(BasicWorkoutInputSerializer):
    class Meta:
        model = Workout
        fields = [
            'id', 'name', 'user', 'sport', 'location', 'location_name', 'start_time', 'description'
        ]


class FullWorkoutSerializer(BasicWorkoutInputSerializer):
    user = MinimalUserSerializer()
    user_list = serializers.SerializerMethodField()

    def get_user_list(self, obj):
        workout = obj.id
        user = obj.user_id
        participants = {
            request.user for request in
            ParticipationRequest.objects
                .filter(workout=workout, status=ACCEPTED)
                .select_related('user')
        }
        owner = User.objects.get(id=user)
        participants.add(owner)
        return MinimalUserSerializer(participants, many=True).data

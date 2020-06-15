import logging
import numpy as np
from django.contrib.gis.db.models.functions import Distance
from django.db.models.functions import Now
from django.utils import timezone
from rest_framework import viewsets, exceptions
from rest_framework.status import HTTP_201_CREATED, HTTP_200_OK
from rest_framework import mixins
from api.models.constants import PENDING
from api.models.user import User
from api.models.participation_request import ParticipationRequest
from api.models.workout import Workout
from api.serializers.participation_request_serializer import ParticipationRequestSerializer, \
    ExpandedParticipationRequestSerializer
from api.models.suggested_workout_history import SuggestedWorkoutHistoryItem
from api.models.user_sport import UserSport
from api.views.suggestions_view_set import generate_workout_model_data, get_global_signed_ratio_squared, \
    get_single_workout_model_data, get_common_workouts
from api.models.ai_model import retrieve_model, update_or_create_model
from random import sample
from api.models.recommendations import model


def filter_chosen_from_suggested(recently_suggested: np.array, chosen_workout: np.array):
    return list(
        filter(lambda x: x[0] != chosen_workout[0], recently_suggested)
    )


def duplicate(x, n):
    return [x for _ in range(n)]


def train_model(recently_suggested: np.array, chosen_workout: np.array, user: User):
    weights = retrieve_model(user.id)
    one_data_in = duplicate(chosen_workout[1:], model.TRAIN_DATA_SIZE)
    filtered_recently_suggested = filter_chosen_from_suggested(recently_suggested, chosen_workout)
    
    if len(filtered_recently_suggested) > model.TRAIN_DATA_SIZE:
        zero_data_in = [
            x[1:] for x in sample(filtered_recently_suggested, model.TRAIN_DATA_SIZE)
        ]
    else:
        zero_data_in = [
            x[1:] for x in filtered_recently_suggested
        ]

    data_in = np.array(one_data_in + zero_data_in)
    data_out = np.array(duplicate(1, len(one_data_in)) + duplicate(0, len(zero_data_in)))
    new_weights = model.train_model(weights, data_in, data_out)
    update_or_create_model(user.id, new_weights)


class ParticipationRequestViewSet(mixins.ListModelMixin,
                                  mixins.CreateModelMixin,
                                  mixins.UpdateModelMixin,
                                  viewsets.GenericViewSet):
    """
    API endpoint that allows users to request participation in a workout
    and workout owners to allow participation.
    """
    serializer_class = ParticipationRequestSerializer
    filterset_fields = ['workout']

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

        if response.status_code == HTTP_201_CREATED:
            user = User.objects.get(id=response.data["user"])
            workout = Workout.objects\
                .annotate(distance=Distance('location', user.location)).get(id=response.data["workout"])
            logging.getLogger('ai_model').info(f'USER JOIN REQUEST: {user.id}, '
                                               f'[{user.location.x}, {user.location.y}], '
                                               f'{response.data["workout"]}')

            recent_workout_ids = SuggestedWorkoutHistoryItem.objects.filter(user=user)
            recent_workouts = Workout.objects.filter(id__in=recent_workout_ids)\
                .annotate(distance=Distance('location', user.location))
            user_sports = UserSport.objects.filter(user=user)
            fullness = get_global_signed_ratio_squared()
            common = get_common_workouts(workout, user)
            common_with_recent = get_common_workouts(recent_workouts, user)
            picked_workout_data = np.array(
                list(get_single_workout_model_data(workout, user, user_sports, fullness, timezone.now(), common))[0]
            )
            data = np.array(list(
                generate_workout_model_data(
                    recent_workouts, user, user_sports, fullness, timezone.now(), common_with_recent
                )
            ))
            train_model(data, picked_workout_data, user)

        return response

    def update(self, request, *args, **kwargs):
        if 'partial' not in kwargs or not kwargs['partial']:
            raise exceptions.MethodNotAllowed(method='PUT')
        else:
            response = super().update(request, *args, **kwargs)

            if response.status_code == HTTP_200_OK:
                user = User.objects.get(id=response.data["user"]["id"])
                logging.getLogger('ai_model').info(f'REQUEST RESPONSE: {response.data["user"]["id"]}, '
                                                   f'[{user.location.x}, {user.location.y}], '
                                                   f'{response.data["status"]}, '
                                                   f'{response.data["workout"]["id"]}')

            return response

    def _remove_disallowed_fields(self, request):
        if self.action == 'create':
            disallowed_fields = {'status', 'seen'}
        elif self.action == 'partial_update':
            disallowed_fields = {'user', 'workout', 'seen'}
        else:
            disallowed_fields = {}

        for field in disallowed_fields:
            if field in request.data:
                del request.data[field]

    def get_serializer_context(self):
        context = super().get_serializer_context()

        request = None
        if 'request' in context:
            request = context['request']
        if not (request and request.data and request.user):
            return context

        request.data['user'] = request.user.user.id
        self._remove_disallowed_fields(request)

        return context

    def get_queryset(self):
        if self.action == 'create':
            return ParticipationRequest.objects.filter(user__id=self.request.user.user.id)
        # only pending approval
        elif self.action == 'list':
            return ParticipationRequest.objects.filter(
                workout__user__id=self.request.user.user.id,
                workout__start_time__gte=Now(),
                status=PENDING
            )
        else:
            return ParticipationRequest.objects.filter(workout__user__id=self.request.user.user.id)

    def get_serializer_class(self):
        if self.action == 'create':
            return ParticipationRequestSerializer
        else:
            return ExpandedParticipationRequestSerializer

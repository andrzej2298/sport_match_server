from django.core.exceptions import ObjectDoesNotExist
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from django.db.models.functions import Now
from django.utils import timezone
from rest_framework import mixins, viewsets

import numpy as np

from api.models.recommendations import model
from api.models.recommendations.model import RECENT_WORKOUTS_DATA_LENGTH, RECENT_WORKOUTS_COUNT
from api.models.constants import SPORTS, MIN_PROFICIENCY_VALUE, MAX_PROFICIENCY_VALUE, EITHER, ACCEPTED
from api.models.workout import Workout
from api.models.user import User
from api.models.user_sport import UserSport
from api.models.participation_request import ParticipationRequest
from api.models.ai_model import retrieve_model
from api.models.suggested_workout_history import SuggestedWorkoutHistoryItem, add_suggested_workout_to_history
from api.serializers.workout_serializer import BasicWorkoutOutputSerializer, get_people_signed_for_a_workout
from api.serializers.suggestion_request_serializer import SuggestionRequestSerializer
from api.utils.time import get_current_age
from api.views.paginators import ResultPagination


MAX_SUGGESTIONS = 30


class SuggestedWorkoutViewSet(mixins.ListModelMixin,
                              viewsets.GenericViewSet):
    """
    API endpoint that allows workout suggestions to be viewed.
    """
    serializer_class = BasicWorkoutOutputSerializer
    filterset_fields = ['sport']
    pagination_class = ResultPagination

    def _initial_workout_filter(self, user, data):
        age = get_current_age(user.birth_date)
        now = Now()

        filtered_workouts = (
            Workout.objects
            .exclude(user=user)
            .filter(
                location__distance_lte=(user.location, D(km=100)),  # user within 100 km of the workout
                start_time__gte=now,  # workout hasn't started yet
                age_min__lte=age,  # at least min age
                age_max__gte=age,  # at most max age
                expected_gender__in=[EITHER, user.gender],  # matching gender
            )
            .exclude(
                id__in=[
                    # if he already asked for participation in a workout, no need do show it a second time
                    p.workout.id
                    for p in ParticipationRequest.objects.filter(user=user)
                ]
            )
            .annotate(distance=Distance('location', user.location))
            .order_by('?')
        )

        if 'sport' in data and data['sport']:
            filtered_workouts = filtered_workouts.filter(sport=data['sport'])
        return filtered_workouts

    def get_queryset(self):
        request_data = self.request.data
        user = User.objects.get(id=self.request.user.user.id)

        serializer = SuggestionRequestSerializer(data=request_data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        filtered_workouts = self._initial_workout_filter(user, data)
        return _get_recommended_workouts(filtered_workouts[:150], user)


def _one_hot(i, value_range):
    array = [0 for _ in range(value_range)]
    array[i] = 1
    return array


def _get_user_proficiency(user_sports, workout_sport_id):
    try:
        return user_sports.get(sport=workout_sport_id).level
    except ObjectDoesNotExist:
        return MIN_PROFICIENCY_VALUE


def _get_workout_has_ben_seen(user: User, workout: dict):
    return int(SuggestedWorkoutHistoryItem.objects.filter(user=user, workout=workout).exists())


_POSSIBLE_PROFICIENCY_VALUES = MAX_PROFICIENCY_VALUE - MIN_PROFICIENCY_VALUE + 1
_POSSIBLE_SPORTS = len(SPORTS)


def get_global_signed_ratio_squared():
    # for recent workouts calculate \frac{1}{N} \sum_{w \in recent}{(signed(w)/max(w))^2}
    # where N is the number of workouts
    recently_ended = Workout.objects.filter(end_time__lte=Now()).order_by('end_time')[:1000].values()

    return sum([
        (get_people_signed_for_a_workout(workout['id']) / workout['people_max']) ** 2
        for workout in recently_ended
    ]) / max(1, len(recently_ended))


def generate_workout_model_data(workouts, user, user_sports, fullness, now, common):
    for w in workouts:
        yield from get_single_workout_model_data(w, user, user_sports, fullness, now, common)


def workout_start_time_key(w):
    return w.start_time


def get_past_workouts_model_data(user, now):
    my_past_participated_workouts = Workout.objects.filter(
            start_time__lte=now,
            id__in=[
                p.workout.id
                for p in ParticipationRequest.objects.filter(user=user)
            ]
        ).order_by('-start_time')[:RECENT_WORKOUTS_COUNT]
    my_past_hosted_workouts = Workout.objects.filter(
        user=user,
        start_time__lte=now
    ).order_by('-start_time')[:RECENT_WORKOUTS_COUNT]
    my_past_workouts = list(my_past_hosted_workouts) + list(my_past_participated_workouts)
    my_past_workouts.sort(key=workout_start_time_key, reverse=True)
    my_past_workouts = my_past_workouts[:RECENT_WORKOUTS_COUNT]
    return_list = []

    for workout in my_past_workouts:
        return_list += [
            *_one_hot(workout.sport_id - 1, _POSSIBLE_SPORTS),
            *_one_hot(workout.desired_proficiency, _POSSIBLE_PROFICIENCY_VALUES),
            (workout.start_time - now).seconds / 60    
        ]

    return_list += [0 for _ in range(RECENT_WORKOUTS_DATA_LENGTH - len(return_list))]

    return return_list


def get_single_workout_model_data(w, user, user_sports, fullness, now, common):
    workout_start_time = w.start_time
    workout_end_time = w.end_time
    workout_location = w.location
    workout_sport_id = w.sport_id
    distance_to_workout = w.distance
    user_proficiency = _get_user_proficiency(user_sports, workout_sport_id)
    workout_has_ben_seen = _get_workout_has_ben_seen(user, w)
    user_location = user.location
    people_signed = get_people_signed_for_a_workout(w.id)
    if people_signed < w.people_max:
        yield [
            w.id,  # workout id
            (workout_start_time - now).seconds / 60,  # minutes to workout
            distance_to_workout.m,  # metres to workout
            workout_location.x,  # workout location x
            workout_location.y,  # workout location y
            user_location.x,  # user location x
            user_location.y,  # user location y
            workout_start_time.hour * 60 + workout_start_time.minute,  # minutes from midnight to start
            workout_end_time.hour * 60 + workout_end_time.minute,  # minutes from midnight to end
            *_one_hot(workout_start_time.weekday(), 7),  # day of the week
            *_one_hot(workout_sport_id - 1, _POSSIBLE_SPORTS),  # sport_id
            *_one_hot(w.desired_proficiency, _POSSIBLE_PROFICIENCY_VALUES),  # workout sport proficiency
            *_one_hot(user_proficiency, _POSSIBLE_PROFICIENCY_VALUES),  # user's proficiency
            w.age_min,
            w.age_max,
            workout_has_ben_seen,
            people_signed,  # people taking part in the workout
            w.people_max,
            common[w.id],
            fullness,
            *get_past_workouts_model_data(user, now)
        ]


def get_workout_recommendations(array: np.array):
    weights = retrieve_model()  # JSON model

    (rows, columns) = array.shape
    selected_columns = [False for _ in range(columns)]
    selected_columns[0] = True  # workout id
    op_selected_columns = [not x for x in selected_columns]
    ids = array[:, selected_columns]
    data = array[:, op_selected_columns]

    # append an extra column with dummy recommendations values
    result = np.ones((rows, 2))
    result[:, :-1] = ids
    result[:, :-2] = model.get_ratings(weights, data)

    return result


def _nested_iterable_to_set(input_iterable):
    result_set = set()
    for nested_list in input_iterable:
        result_set |= set(nested_list)
    return result_set


def get_common_workouts(filtered_workouts, user):
    if isinstance(filtered_workouts, Workout):
        filtered_workouts = [filtered_workouts]
    # with how many users in this workout do I have a common workout
    result = {}

    participants, participant_ids = _participant_ids(filtered_workouts)

    # ways in which a current user A can have a common workout with another user B
    # 1. A hosts a workout to which B is allowed
    # 2. B hosts a workout to which A is allowed
    # 3. A and B are allowed to take part in a workout
    #    none of them is hosting

    # participants of workouts the user has created, satisfies case 1.
    users_hosted_workout_participants = _nested_iterable_to_set([
        [p.user.id for p in w.participationrequest_set.filter(status=ACCEPTED, user__in=participant_ids)]
        for w in user.workout_set.all()
    ])

    # workouts the user been allowed to participate in, satisfies cases 2. and 3.
    users_accepted_workouts = _nested_iterable_to_set([
        # case 2.
        [p.workout.user.id] + [
            # case 3.
            q.user.id
            for q in p
                .workout
                .participationrequest_set
                .filter(status=ACCEPTED, user__in=participant_ids)
        ] for p in user.participationrequest_set.filter(status=ACCEPTED)
    ])

    users_participating_in_common_workouts = users_hosted_workout_participants | users_accepted_workouts

    for workout in filtered_workouts:
        result[workout.id] = len(participants[workout.id] & users_participating_in_common_workouts)

    return result


def _participant_ids(filtered_workouts):
    # participants in suggested workouts mapping
    participants = {
        w.id: {w.user.id} | {
            p.user.id for p in w.participationrequest_set.filter(status=ACCEPTED)
        }
        for w in filtered_workouts
    }
    # participants in suggested workouts ids
    participant_ids = _nested_iterable_to_set(participants.values())
    return participants, participant_ids


def _get_recommended_workouts(workouts, user):
    user_sports = UserSport.objects.filter(user=user)
    fullness = get_global_signed_ratio_squared()

    common = get_common_workouts(workouts, user)
    filtered = np.array(list(
        generate_workout_model_data(workouts, user, user_sports, fullness, timezone.now(), common)
    ))

    # no suggestions, prevent accessing non existent columns
    if filtered.size == 0:
        return Workout.objects.none()

    from sys import stderr
    print(filtered.ndim, file=stderr)
    recommended = get_workout_recommendations(filtered)

    # sort recommendations by value
    sorted_by_recommendation_value = recommended[recommended[:, 1].argsort()][::-1]
    # convert back to ints (numpy stored ids as floats)
    recommended_ids = {int(workout_id) for workout_id in sorted_by_recommendation_value[:MAX_SUGGESTIONS, 0].tolist()}
    # cannot filter the queryset directly, because it already has been sliced before
    recommended_workouts = Workout.objects.filter(id__in=recommended_ids)

    # update recommendation history in the database
    for workout_id in recommended_workouts:
        add_suggested_workout_to_history(workout_id, user)

    return recommended_workouts

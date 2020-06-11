import logging
from rest_framework import mixins, viewsets
from rest_framework.status import HTTP_201_CREATED
from django_filters.rest_framework import FilterSet, IsoDateTimeFromToRangeFilter
from api.models.workout import Workout
from api.models.participation_request import ParticipationRequest
from api.serializers.workout_serializer import FullWorkoutSerializer, BasicWorkoutInputSerializer
from api.models.constants import PENDING, ACCEPTED, REJECTED


class DateFilter(FilterSet):
    start_time = IsoDateTimeFromToRangeFilter()

    class Meta:
        model = Workout
        fields = ['start_time']


class HostedWorkoutViewSet(mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           mixins.CreateModelMixin,
                           mixins.UpdateModelMixin,
                           viewsets.GenericViewSet):
    """
    API endpoint that allows workouts hosted by user to be viewed or edited.
    """
    filter_class = DateFilter

    def create(self, request, *args, **kwargs):
        request.data['user'] = request.user.user.id
        response = super().create(request, *args, **kwargs)

        if response.status_code == HTTP_201_CREATED:
            logging.getLogger('ai_model').info(f'WORKOUT {response.data["id"]} CREATED')

        return response

    def get_queryset(self):
        return Workout.objects.filter(user__id=self.request.user.user.id)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return FullWorkoutSerializer
        else:
            return BasicWorkoutInputSerializer


def get_request_related_workouts(**kwargs):
    workouts = {
        request.workout for request in
        ParticipationRequest.objects.filter(**kwargs).select_related('workout')
    }
    return workouts


class PendingWorkoutViewSet(mixins.ListModelMixin,
                            viewsets.GenericViewSet):
    """
    API endpoint that allows workouts pending approval to be viewed or edited.
    """
    serializer_class = FullWorkoutSerializer

    def get_queryset(self):
        return get_request_related_workouts(user__id=self.request.user.user.id, status=PENDING)


class RecentlyAcceptedWorkoutViewSet(mixins.ListModelMixin,
                                     viewsets.GenericViewSet):
    """
    API endpoint that allows recently accepted workouts to be viewed or edited.
    """
    serializer_class = FullWorkoutSerializer

    def get_queryset(self):
        user_id = self.request.user.user.id
        relevant_requests = ParticipationRequest.objects.filter(user__id=user_id, status=ACCEPTED, seen=False)
        recently_accepted = {
            request.workout for request in relevant_requests.select_related('workout')
        }

        relevant_requests.update(seen=True)

        return recently_accepted


class RecentlyRejectedWorkoutViewSet(mixins.ListModelMixin,
                                     viewsets.GenericViewSet):
    """
    API endpoint that allows recently rejected workouts to be viewed or edited.
    """
    serializer_class = FullWorkoutSerializer

    def get_queryset(self):
        user_id = self.request.user.user.id
        relevant_requests = ParticipationRequest.objects.filter(user__id=user_id, status=REJECTED, seen=False)
        recently_accepted = {
            request.workout for request in relevant_requests.select_related('workout')
        }
        relevant_requests.update(seen=True)

        return recently_accepted


class WorkoutViewSet(mixins.RetrieveModelMixin,
                     mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    """
    API endpoint that allows a list of the workouts a particular user is
    going to take part in to be viewed.
    Also, any workout by any user can be viewed by id.
    Filtering by date and time is allowed.
    """
    filter_class = DateFilter

    def get_queryset(self):
        if self.action == 'list':
            user_id = self.request.user.user.id
            hosted = Workout.objects.filter(user__id=user_id)

            accepted_requests = [
                request.workout.id
                for request in ParticipationRequest.objects.filter(user__id=user_id, status=ACCEPTED)
            ]
            # filtering after union is not allowed, so filter_queryset has to be applied here
            taking_part_in = Workout.objects.filter(id__in=accepted_requests)

            return hosted | taking_part_in
        elif self.action == 'retrieve':
            return Workout.objects.all()

    def get_serializer_class(self):
        # TODO permissions
        return FullWorkoutSerializer

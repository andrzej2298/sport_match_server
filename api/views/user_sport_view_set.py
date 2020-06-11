from rest_framework import viewsets
from api.models.user_sport import UserSport
from api.serializers.user_sport_serializer import UserSportSerializer


class UserSportViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows user's sports to be viewed or edited.
    """
    serializer_class = UserSportSerializer

    def create(self, request, *args, **kwargs):
        request.data['user'] = request.user.user.id
        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        return UserSport.objects.filter(user__id=self.request.user.user.id)

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from api.models.user import User
from api.serializers.user_serializer import UserSerializer, OtherUserSerializer
from rest_framework.permissions import AllowAny
from rest_framework import mixins


# TODO permissions
class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = User.objects.all()
    serializer_class = OtherUserSerializer

    @action(methods=['get'], detail=False)
    def me(self, request):
        user = request.user.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def update_me(self, request, *args, **kwargs):
        instance = request.user.user
        serializer = UserSerializer(instance, data=request.data, partial=kwargs['partial'])
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    @me.mapping.patch
    def partial_update_me(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update_me(request, *args, **kwargs)

    @me.mapping.put
    def full_update_me(self, request, *args, **kwargs):
        kwargs['partial'] = False
        return self.update_me(request, *args, **kwargs)


class CreateUserViewSet(mixins.CreateModelMixin,
                        viewsets.GenericViewSet):
    permission_classes = [AllowAny]

    queryset = User.objects.all()
    serializer_class = UserSerializer

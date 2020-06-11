from rest_framework import viewsets
from api.models.sport import Sport
from api.serializers.sport_serializer import SportSerializer


class SportViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows sports to be viewed.
    """

    queryset = Sport.objects.all()
    serializer_class = SportSerializer

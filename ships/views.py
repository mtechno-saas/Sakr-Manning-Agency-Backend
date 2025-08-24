from rest_framework import viewsets
from .models import Ship
from .serializers import ShipSerializer

class ShipViewSet(viewsets.ModelViewSet):
    queryset = Ship.objects.all()
    serializer_class = ShipSerializer

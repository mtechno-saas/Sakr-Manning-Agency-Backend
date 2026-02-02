from django.shortcuts import render

# Create your views here.
# core/views.py
from rest_framework import viewsets
from .models import Flag, VesselType
from .serializers import FlagSerializer, VesselTypeSerializer 


class FlagViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Flags to be viewed or edited.
    """
    queryset = Flag.objects.all()
    serializer_class = FlagSerializer

class VesselTypeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Vessel Types to be viewed or edited.
    """
    queryset = VesselType.objects.all()
    serializer_class = VesselTypeSerializer

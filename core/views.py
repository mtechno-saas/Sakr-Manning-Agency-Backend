from django.shortcuts import render

# Create your views here.
# core/views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Flag, VesselType, CompanyType
from .serializers import FlagSerializer, VesselTypeSerializer, CompanyTypeSerializer 


class FlagViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Flags to be viewed or edited.
    """
    queryset = Flag.objects.all()
    serializer_class = FlagSerializer
    permission_classes = [IsAuthenticated]

class VesselTypeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Vessel Types to be viewed or edited.
    """
    queryset = VesselType.objects.all()
    serializer_class = VesselTypeSerializer
    permission_classes = [IsAuthenticated]

class CompanyTypeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Company Types to be viewed or edited.
    """
    queryset = CompanyType.objects.all()
    serializer_class = CompanyTypeSerializer
    permission_classes = [IsAuthenticated]

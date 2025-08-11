from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from . models import *
from . serializer import *
# Create your views here.


@api_view(['GET'])
def get_all_users(request):
    users = Man.objects.all()
    serializer = ManSerializer(users , many=True)
    #print(serializer.data)
    return Response({"users":serializer.data})
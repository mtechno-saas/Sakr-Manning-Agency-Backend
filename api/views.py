from django.shortcuts import render
from rest_framework.decorators import api_view ,parser_classes
from rest_framework.parsers import MultiPartParser , FormParser
from rest_framework.response import Response
from rest_framework import status
from . models import *
from . serializer import *
# Create your views here.


@api_view(['GET'])
def get_all_users(request):
    users = Users.objects.all()
    serializer = ManSerializer(users , many=True)
    #print(serializer.data)
    return Response({"users":serializer.data})




@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])   # Allow file + form upload
def create_user(request):
    serializer = UsersSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    print(request.content_type)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
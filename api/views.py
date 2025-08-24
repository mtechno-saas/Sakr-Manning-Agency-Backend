from django.shortcuts import render , get_object_or_404
from rest_framework.decorators import api_view ,parser_classes
from rest_framework.parsers import MultiPartParser , FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from rest_framework.response import Response
from rest_framework import status
from . models import *
from . serializer import  UsersSerializer , ManSerializer 
from rest_framework import viewsets
from .filters import UsersFilter
from rest_framework import viewsets
#from . import UserSerializer 

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




@api_view(['GET'])
def users_list_id(request,pk):
    user = get_object_or_404(Users , id=pk)
    serializer = UsersSerializer(user, many=False)

    return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(['GET'])
def get_filter_users(request):
    #users = Users.objects.all()
    filter_set = UsersFilter(request.GET, queryset=Users.objects.all().order_by("id"))
    serializer = UsersSerializer(filter_set.qs , many=True)
    #print(serializer.data)
    return Response({"users":serializer.data})



class UserViewSet(viewsets.ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer
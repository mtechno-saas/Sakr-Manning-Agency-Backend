# from django.shortcuts import render , get_object_or_404
# from rest_framework.decorators import api_view ,parser_classes
# from rest_framework.parsers import MultiPartParser , FormParser
# from django_filters.rest_framework import DjangoFilterBackend
# from django_filters import rest_framework as filters
# from rest_framework.response import Response
# from rest_framework import status
# from . models import *
# from . serializer import  UsersSerializer , ManSerializer , UserRankSerializer

# from rest_framework import viewsets
# from .filters import UsersFilter

# #from . import UserSerializer 

# # Create your views here.


# @api_view(['GET'])
# def get_all_users(request):
#     users = Users.objects.all()
#     serializer = ManSerializer(users , many=True)
#     #print(serializer.data)
#     return Response({"users":serializer.data})




# # @api_view(["POST"])
# # @parser_classes([MultiPartParser, FormParser])   # Allow file + form upload
# # def create_user(request):
# #     serializer = UserSerializer(data=request.data)
# #     if serializer.is_valid():
# #         serializer.save()
# #         return Response(serializer.data, status=status.HTTP_201_CREATED)
# #     print(request.content_type)
# #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @api_view(["POST"])
# def create_user(request):
#     serializer = UsersSerializer(data=request.data)
#     if serializer.is_valid():
#         user = serializer.save()

#         # if you pass codes (list of IDs) in request.data
#         codes = request.data.get("codes", [])
#         if codes:
#             user.codes.set(codes)   # ✅ correct way
#             user.save()

#         return Response(UsersSerializer(user).data, status=201)
#     return Response(serializer.errors, status=400)






# @api_view(['GET'])
# def users_list_id(request,pk):
#     user = get_object_or_404(Users , id=pk)
#     serializer = UsersSerializer(user, many=False)

#     return Response(serializer.data, status=status.HTTP_200_OK)



# @api_view(['GET'])
# def get_filter_users(request):
#     #users = Users.objects.all()
#     filter_set = UsersFilter(request.GET, queryset=Users.objects.all().order_by("id"))
#     serializer = UsersSerializer(filter_set.qs , many=True)
#     #print(serializer.data)
#     return Response({"users":serializer.data})


# @api_view(["POST"])
# def assign_rank(request, user_id, rank_id):
#     try:
#         user = Users.objects.get(pk=user_id)
#         rank = Rank.objects.get(pk=rank_id)
#     except (Users.DoesNotExist, Rank.DoesNotExist):
#         return Response({"error": "User or Rank not found"}, status=status.HTTP_404_NOT_FOUND)

#     # Create UserRank (auto-increments code)
#     user_rank = UserRank.objects.create(user=user, rank=rank)
#     serializer = UserRankSerializer(user_rank)
#     return Response(serializer.data, status=status.HTTP_201_CREATED)



# class UserViewSet(viewsets.ModelViewSet):
#     queryset = Users.objects.all()
#     serializer_class = UsersSerializer

# # api/views.py
# from django.shortcuts import get_object_or_404
# from rest_framework.decorators import api_view, parser_classes
# from rest_framework.parsers import MultiPartParser, FormParser
# from rest_framework.response import Response
# from rest_framework import status, viewsets
# from .models import Users, Rank, UserRank
# from .serializer import UsersSerializer, UserRankSerializer
# from .filters import UsersFilter


# @api_view(['GET'])
# def get_all_users(request):
#     users = Users.objects.all()
#     # Note: Using UsersSerializer now instead of ManSerializer for consistency
#     serializer = UsersSerializer(users, many=True)
#     return Response({"users": serializer.data})


# @api_view(["POST"])
# @parser_classes([MultiPartParser, FormParser]) # Keep parsers for profile image uploads
# def create_user(request):
#     # The logic is now handled inside the serializer
#     serializer = UsersSerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['GET'])
# def users_list_id(request, pk):
#     user = get_object_or_404(Users, id=pk)
#     serializer = UsersSerializer(user, many=False)
#     return Response(serializer.data, status=status.HTTP_200_OK)


# @api_view(['GET'])
# def get_filter_users(request):
#     filter_set = UsersFilter(request.GET, queryset=Users.objects.all().order_by("id"))
#     serializer = UsersSerializer(filter_set.qs, many=True)
#     return Response({"users": serializer.data})


# @api_view(["POST"])
# def assign_rank(request, user_id, rank_id):
#     try:
#         user = Users.objects.get(pk=user_id)
#         rank = Rank.objects.get(pk=rank_id)
#     except (Users.DoesNotExist, Rank.DoesNotExist):
#         return Response({"error": "User or Rank not found"}, status=status.HTTP_404_NOT_FOUND)

#     user_rank = UserRank.objects.create(user=user, rank=rank)
#     serializer = UserRankSerializer(user_rank)
#     return Response(serializer.data, status=status.HTTP_201_CREATED)


# class UserViewSet(viewsets.ModelViewSet):
#     queryset = Users.objects.all()
#     serializer_class = UsersSerializer


# api/views.py
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status, viewsets
from .models import Users, Rank, UserRank
from .serializer import UsersSerializer, UserRankSerializer
# Import the filter class you just created
from .filters import UsersFilter


@api_view(['GET'])
def get_all_users(request):
    users = Users.objects.all()
    serializer = UsersSerializer(users, many=True)
    return Response({"users": serializer.data})


@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def create_user(request):
    serializer = UsersSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def users_list_id(request, pk):
    user = get_object_or_404(Users, id=pk)
    serializer = UsersSerializer(user, many=False)
    return Response(serializer.data, status=status.HTTP_200_OK)


# This is the view that uses your filter
@api_view(['GET'])
def get_filter_users(request):
    """
    A view that filters users based on query parameters.
    """
    # Use the UsersFilter class to filter the queryset
    filterset = UsersFilter(request.GET, queryset=Users.objects.prefetch_related('user_ranks__rank', 'certificates').all().order_by("id"))
    
    serializer = UsersSerializer(filterset.qs, many=True)
    return Response({"users": serializer.data})


@api_view(["POST"])
def assign_rank(request, user_id, rank_id):
    try:
        user = Users.objects.get(pk=user_id)
        rank = Rank.objects.get(pk=rank_id)
    except (Users.DoesNotExist, Rank.DoesNotExist):
        return Response({"error": "User or Rank not found"}, status=status.HTTP_404_NOT_FOUND)

    user_rank = UserRank.objects.create(user=user, rank=rank)
    serializer = UserRankSerializer(user_rank)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserViewSet(viewsets.ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer
    # You can also integrate filtering directly into a ViewSet like this
    # filterset_class = UsersFilter



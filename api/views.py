
# api/views.py
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework import status, viewsets, generics
from rest_framework.permissions import AllowAny
from .models import Users, Rank, UserRank, Contract, Reference, SeaService, Certificate
from .serializer import (
    UsersSerializer, UserRankSerializer, ContractSerializer, 
    ReferenceSerializer, SeaServiceSerializer, CertificateSerializer, 
    RankSerializer, RegisterSerializer
)
from .filters import UsersFilter
from .permissions import IsHROrReadOnly
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.response import Response

from .models import Users
from .permissions import IsHROrReadOnly
from .serializer import UsersSerializer
from .serializer import UserMeSerializer



class RegisterView(generics.CreateAPIView):
    queryset = Users.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        serializer = UserMeSerializer(request.user)
        return Response(serializer.data)

# --- List and Create Views ---

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
def get_filter_users(request):
    filterset = UsersFilter(request.GET, queryset=Users.objects.prefetch_related('user_ranks__rank', 'certificates').all().order_by("id"))
    serializer = UsersSerializer(filterset.qs, many=True)
    return Response({"users": serializer.data})


# --- Detail, Update, and Delete View ---

@api_view(['GET', 'PUT', 'DELETE'])
def user_detail(request, pk):
    """
    Retrieve, update or delete a user instance.
    """
    user = get_object_or_404(Users, id=pk)

    if request.method == 'GET':
        serializer = UsersSerializer(user)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = UsersSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# --- Other Views ---

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


class ContractViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing seafarer contracts.
    """
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer


class ReferenceViewSet(viewsets.ModelViewSet):
    queryset = Reference.objects.all()
    serializer_class = ReferenceSerializer


class SeaServiceViewSet(viewsets.ModelViewSet):
    queryset = SeaService.objects.all()
    serializer_class = SeaServiceSerializer


class CertificateViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing certificates.
    """
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer


class RankViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing ranks.
    """
    queryset = Rank.objects.all()
    serializer_class = RankSerializer


# --- User-specific Certificate and Rank Endpoints ---

@api_view(['GET'])
def get_user_certificates(request, user_id):
    """
    Get all certificates that a specific user has taken.
    """
    try:
        user = Users.objects.get(pk=user_id)
    except Users.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    
    certificates = user.certificates.all()
    serializer = CertificateSerializer(certificates, many=True)
    return Response({
        "user_id": user_id,
        "user_name": f"{user.first_name} {user.middle_name}",
        "certificates": serializer.data
    })


@api_view(['GET'])
def get_user_ranks(request, user_id):
    """
    Get all ranks that a specific user wants to apply for (has been assigned).
    """
    try:
        user = Users.objects.get(pk=user_id)
    except Users.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    
    user_ranks = UserRank.objects.filter(user=user).select_related('rank')
    serializer = UserRankSerializer(user_ranks, many=True)
    return Response({
        "user_id": user_id,
        "user_name": f"{user.first_name} {user.middle_name}",
        "ranks": serializer.data
    })


@api_view(['POST'])
def add_user_certificate(request, user_id):
    """
    Add a certificate to a user.
    Expected payload: {"certificate_id": 1}
    """
    try:
        user = Users.objects.get(pk=user_id)
    except Users.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    
    certificate_id = request.data.get('certificate_id')
    if not certificate_id:
        return Response({"error": "certificate_id is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        certificate = Certificate.objects.get(pk=certificate_id)
    except Certificate.DoesNotExist:
        return Response({"error": "Certificate not found"}, status=status.HTTP_404_NOT_FOUND)
    
    user.certificates.add(certificate)
    return Response({
        "message": f"Certificate '{certificate.name}' added to user {user.first_name} {user.middle_name}",
        "certificate": CertificateSerializer(certificate).data
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def add_user_rank(request, user_id):
    """
    Add a rank to a user (rank they want to apply for).
    Expected payload: {"rank_id": 1}
    """
    try:
        user = Users.objects.get(pk=user_id)
    except Users.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    
    rank_id = request.data.get('rank_id')
    if not rank_id:
        return Response({"error": "rank_id is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        rank = Rank.objects.get(pk=rank_id)
    except Rank.DoesNotExist:
        return Response({"error": "Rank not found"}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if user already has this rank
    if UserRank.objects.filter(user=user, rank=rank).exists():
        return Response({"error": "User already has this rank"}, status=status.HTTP_400_BAD_REQUEST)
    
    user_rank = UserRank.objects.create(user=user, rank=rank)
    serializer = UserRankSerializer(user_rank)
    return Response({
        "message": f"Rank '{rank.name}' added to user {user.first_name} {user.middle_name}",
        "user_rank": serializer.data
    }, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
def remove_user_certificate(request, user_id, certificate_id):
    """
    Remove a certificate from a user.
    """
    try:
        user = Users.objects.get(pk=user_id)
        certificate = Certificate.objects.get(pk=certificate_id)
    except Users.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    except Certificate.DoesNotExist:
        return Response({"error": "Certificate not found"}, status=status.HTTP_404_NOT_FOUND)
    
    user.certificates.remove(certificate)
    return Response({
        "message": f"Certificate '{certificate.name}' removed from user {user.first_name} {user.middle_name}"
    }, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def remove_user_rank(request, user_id, rank_id):
    """
    Remove a rank from a user.
    """
    try:
        user = Users.objects.get(pk=user_id)
        rank = Rank.objects.get(pk=rank_id)
    except Users.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    except Rank.DoesNotExist:
        return Response({"error": "Rank not found"}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        user_rank = UserRank.objects.get(user=user, rank=rank)
        user_rank.delete()
        return Response({
            "message": f"Rank '{rank.name}' removed from user {user.first_name} {user.middle_name}"
        }, status=status.HTTP_200_OK)
    except UserRank.DoesNotExist:
        return Response({"error": "User does not have this rank"}, status=status.HTTP_404_NOT_FOUND)
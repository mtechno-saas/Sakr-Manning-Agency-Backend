


# api/views.py
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status , viewsets
from .models import Users, Rank, UserRank , Contract
from .serializer import UsersSerializer, UserRankSerializer , ContractSerializer
from .filters import UsersFilter
from .permissions import IsHROrReadOnly # <-- Import the permission
from rest_framework.parsers import MultiPartParser, FormParser 
from rest_framework.permissions import AllowAny # <-- Import AllowAny
from .serializer import RegisterSerializer # <-- Import your new serializer
from rest_framework import generics



class RegisterView(generics.CreateAPIView):
    queryset = Users.objects.all()
    permission_classes = (AllowAny,) # <-- This makes the endpoint public
    serializer_class = RegisterSerializer

class UserViewSet(viewsets.ModelViewSet): # <-- I'm assuming you have a UserViewSet, if not, apply this to your user views
    queryset = Users.objects.all()
    serializer_class = UsersSerializer
    permission_classes = [IsHROrReadOnly] # <-- Use the permission class
    parser_classes = [MultiPartParser, FormParser]


class UserViewSet(viewsets.ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer

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

# --- Detail, Update, and Delete View (New/Modified) ---

@api_view(['GET', 'PUT', 'DELETE'])
def user_detail(request, pk):
    """
    Retrieve, update or delete a user instance.
    """
    user = get_object_or_404(Users, id=pk)

    if request.method == 'GET':
        # This replaces your old users_list_id view
        serializer = UsersSerializer(user)
        return Response(serializer.data)

    elif request.method == 'PUT':
        # This is the new Edit/Update functionality
        serializer = UsersSerializer(user, data=request.data, partial=True) # partial=True allows partial updates
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # This is the new Delete functionality
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
    # Add permissions, e.g., only HR or Admins can create/edit contracts
    # permission_classes = [IsAdminUser] 
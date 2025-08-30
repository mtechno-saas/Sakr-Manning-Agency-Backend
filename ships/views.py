

# ships/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Ship
from .serializers import ShipSerializer
from .permissions import IsShipManagerOrAdmin 
# Import the Users model to fetch the user object
from api.models import Users

class ShipViewSet(viewsets.ModelViewSet):
    queryset = Ship.objects.all()
    serializer_class = ShipSerializer

    # This decorator creates a new endpoint: /api/ships/{ship_pk}/assign_user/
    @action(detail=True, methods=['post'], url_path='assign-user')
    def assign_user(self, request, pk=None):
        """
        Assigns a user to the ship's crew.
        Expects a 'user_id' in the request body.
        """
        # Get the specific ship instance using the primary key from the URL
        ship = self.get_object()

        # Get the user_id from the request data
        user_id = request.data.get('user_id')

        if not user_id:
            return Response(
                {'error': 'user_id must be provided in the request body.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Find the user to be added
            user_to_assign = Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            return Response(
                {'error': 'User not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Add the user to the ship's crew
        # ManyToManyFields have an .add() method
        ship.crew.add(user_to_assign)

        # Return a success response
        return Response(
            {'status': f'User {user_to_assign.first_name} assigned to ship {ship.ship_name}'},
            status=status.HTTP_200_OK
        )

    # We can also add an endpoint to unassign a user
    @action(detail=True, methods=['post'], url_path='unassign-user')
    def unassign_user(self, request, pk=None):
        """
        Removes a user from the ship's crew.
        Expects a 'user_id' in the request body.
        """
        ship = self.get_object()
        user_id = request.data.get('user_id')

        if not user_id:
            return Response({'error': 'user_id must be provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_to_unassign = Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Use the .remove() method for ManyToManyFields
        ship.crew.remove(user_to_unassign)

        return Response(
            {'status': f'User {user_to_unassign.first_name} unassigned from ship {ship.ship_name}'},
            status=status.HTTP_200_OK
        )

class ShipViewSet(viewsets.ModelViewSet):
    """
    How It Works Now
Anonymous User: Cannot access any endpoint (gets a 401 Unauthorized error).
Authenticated User (No Group): Can view the list of ships and users, but if they try to POST (create) or PUT (edit) a ship, 
they will get a 403 Forbidden error with the message "You do not have permission to perform this action."
User in "HR" Group: Can view, create, and edit users. They can only view ships.
User in "Ship Manager" Group: Can view, create, and edit ships. They can only view users.
User in "Admin" Group (or Superuser): Can do everything.
You have now successfully implemented a flexible and powerful role-based permission system for your API. 
You can create as many roles and as many custom permission classes as you need to model your business logic.
    """
    queryset = Ship.objects.all()
    serializer_class = ShipSerializer
    permission_classes = [IsShipManagerOrAdmin] # <-- Use the permission class


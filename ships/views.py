from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Ship
from .serializers import ShipSerializer
from .permissions import IsShipManagerOrAdmin 
from api.models import Users
from api.filters import ShipFilter

class ShipViewSet(viewsets.ModelViewSet):
    """
    Manages Ships.
    Role-based access:
    - Admin/Ship Manager: Full access
    - Others: Read-only or restricted
    """
    queryset = Ship.objects.select_related('company', 'flag', 'ship_type').prefetch_related('crew').all()
    serializer_class = ShipSerializer
    permission_classes = [IsShipManagerOrAdmin]
    filterset_class = ShipFilter

    @action(detail=True, methods=['post'], url_path='assign-user')
    def assign_user(self, request, pk=None):
        """
        Assigns a user to the ship's crew.
        Expects 'user_id' in body.
        """
        ship = self.get_object()
        user_id = request.data.get('user_id')

        if not user_id:
            return Response({'error': 'user_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        ship.crew.add(user)

        # Update the targeted (latest) CV submission
        from api.models import CVSubmission, Contract
        latest_cv = CVSubmission.objects.filter(user=user).order_by('-submitted_date').first()
        if latest_cv:
            latest_cv.ship = ship
            latest_cv.save(update_fields=['ship'])

        # Update the targeted (latest) Contract
        latest_contract = Contract.objects.filter(user=user).order_by('-created_at').first()
        if latest_contract:
            latest_contract.ship = ship
            latest_contract.save(update_fields=['ship'])

        return Response(
            {'status': f'User {user.first_name} assigned to {ship.ship_name}'},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'], url_path='unassign-user')
    def unassign_user(self, request, pk=None):
        """
        Removes a user from the ship's crew.
        Expects 'user_id' in body.
        """
        ship = self.get_object()
        user_id = request.data.get('user_id')

        if not user_id:
            return Response({'error': 'user_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        ship.crew.remove(user)
        return Response(
            {'status': f'User {user.first_name} unassigned from {ship.ship_name}'},
            status=status.HTTP_200_OK
        )

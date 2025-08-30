# from django.shortcuts import render

# # Create your views here.


# from rest_framework.decorators import api_view, parser_classes
# from rest_framework.parsers import MultiPartParser, FormParser
# from rest_framework.response import Response
# from rest_framework import status
# from .models import TravelingPaper, Ticket
# from .serializers import TravelingPaperSerializer, TicketSerializer

# # ---- Traveling Papers ----
# @api_view(['POST'])
# @parser_classes([MultiPartParser, FormParser])
# def create_traveling_paper(request):
#     serializer = TravelingPaperSerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['GET'])
# def list_traveling_papers(request, user_id):
#     papers = TravelingPaper.objects.filter(user_id=user_id)
#     serializer = TravelingPaperSerializer(papers, many=True)
#     return Response(serializer.data)


# # ---- Tickets ----
# @api_view(['POST'])
# @parser_classes([MultiPartParser, FormParser])
# def create_ticket(request):
#     serializer = TicketSerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['GET'])
# def list_tickets(request, user_id):
#     tickets = Ticket.objects.filter(user_id=user_id)
#     serializer = TicketSerializer(tickets, many=True)
#     return Response(serializer.data)


# tickets_papers/views.py
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Ticket, TravelingPaper
from .serializers import TicketSerializer, TravelingPaperSerializer
from api.models import Users # We'll need this for associating the user

class TicketViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing, creating, and deleting Tickets for a specific user.
    """
    serializer_class = TicketSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        """
        This view should only return tickets for the user specified in the URL.
        """
        # We access the user's ID from the URL kwargs, which is populated by the nested router.
        user_pk = self.kwargs['user_pk']
        return Ticket.objects.filter(user__pk=user_pk)

    def perform_create(self, serializer):
        """
        When creating a new ticket, automatically associate it with the user
        from the URL.
        """
        user = Users.objects.get(pk=self.kwargs['user_pk'])
        # The serializer is saved with the user instance, so we don't need
        # to pass the user_id in the request body.
        serializer.save(user=user)


class TravelingPaperViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing, creating, and deleting Traveling Papers for a specific user.
    """
    serializer_class = TravelingPaperSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        """
        This view should only return papers for the user specified in the URL.
        """
        user_pk = self.kwargs['user_pk']
        return TravelingPaper.objects.filter(user__pk=user_pk)

    def perform_create(self, serializer):
        """
        When creating a new paper, automatically associate it with the user
        from the URL.
        """
        user = Users.objects.get(pk=self.kwargs['user_pk'])
        serializer.save(user=user)

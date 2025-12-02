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

class TicketViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing, creating, and deleting Tickets.
    """
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        """
        Optionally filter tickets by user_id query parameter.
        """
        queryset = Ticket.objects.all()
        user_id = self.request.query_params.get('user_id', None)
        if user_id is not None:
            queryset = queryset.filter(user__pk=user_id)
        return queryset


class TravelingPaperViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing, creating, and deleting Traveling Papers.
    """
    queryset = TravelingPaper.objects.all()
    serializer_class = TravelingPaperSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        """
        Optionally filter traveling papers by user_id query parameter.
        """
        queryset = TravelingPaper.objects.all()
        user_id = self.request.query_params.get('user_id', None)
        if user_id is not None:
            queryset = queryset.filter(user__pk=user_id)
        return queryset


# from django.urls import path
# from . import views

# urlpatterns = [
#     # Traveling Papers
#     path("papers/create/", views.create_traveling_paper, name="create_traveling_paper"),
#     path("papers/<int:user_id>/", views.list_traveling_papers, name="list_traveling_papers"),

#     # Tickets
#     path("tickets/create/", views.create_ticket, name="create_ticket"),
#     path("tickets/<int:user_id>/", views.list_tickets, name="list_tickets"),
# ]
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TicketViewSet, TravelingPaperViewSet

# Create a router
router = DefaultRouter()

# Register the ViewSets with the router
# This will create URLs like /tickets/ and /tickets/{id}/
router.register(r'tickets', TicketViewSet, basename='ticket')
router.register(r'traveling-papers', TravelingPaperViewSet, basename='traveling-paper')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]
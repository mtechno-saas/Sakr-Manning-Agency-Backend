# from django.urls import path
# from . import views

# urlpatterns = [
#     path('papers/create/', views.create_traveling_paper, name='create_traveling_paper'),
#     path('papers/<int:user_id>/', views.list_traveling_papers, name='list_traveling_papers'),
#     path('tickets/create/', views.create_ticket, name='create_ticket'),
#     path('tickets/<int:user_id>/', views.list_tickets, name='list_tickets'),
# ]

from django.urls import path
from . import views

urlpatterns = [
    # Traveling Papers
    path("papers/create/", views.create_traveling_paper, name="create_traveling_paper"),
    path("papers/<int:user_id>/", views.list_traveling_papers, name="list_traveling_papers"),

    # Tickets
    path("tickets/create/", views.create_ticket, name="create_ticket"),
    path("tickets/<int:user_id>/", views.list_tickets, name="list_tickets"),
]

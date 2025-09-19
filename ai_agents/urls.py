# ai_agents/urls.py
from django.urls import path
from .views import ShipAIView

urlpatterns = [
    path("ships/", ShipAIView.as_view(), name="ship-ai"),
]

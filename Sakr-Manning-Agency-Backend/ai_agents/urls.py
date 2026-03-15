# ai_agents/urls.py
from django.urls import path
from .views import ChatSearchView, ChatHistoryView, UserSessionsView, SearchCapabilitiesView

urlpatterns = [
    path('chat/', ChatSearchView.as_view(), name='chat_search'),
    path('chat/history/<uuid:session_id>/', ChatHistoryView.as_view(), name='chat_history'),
    path('chat/sessions/', UserSessionsView.as_view(), name='user_sessions'),
    path('capabilities/', SearchCapabilitiesView.as_view(), name='search_capabilities'),
]
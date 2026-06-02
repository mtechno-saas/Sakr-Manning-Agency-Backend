# from django.shortcuts import render

# # Create your views here.
# # ai_agents/views.py
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from .agent import agent
# from .serializers import ShipSerializer, UserSerializer
# from ships.models import Ship
# from api.models import Users

# class ShipAIView(APIView):
#     """
#     AI-powered ship and crew management.
#     """

#     def post(self, request, *args, **kwargs):
#         query = request.data.get("query")
#         if not query:
#             return Response({"error": "No query provided"}, status=status.HTTP_400_BAD_REQUEST)
        
#         try:
#             result = agent.run(query)

#             # Structured dict result from tools
#             if isinstance(result, dict):
#                 if "ship_id" in result:
#                     ship = Ship.objects.get(id=result["ship_id"])
#                     return Response(ShipSerializer(ship).data, status=status.HTTP_200_OK)
#                 if "user_id" in result:
#                     user = Users.objects.get(id=result["user_id"])
#                     return Response(UserSerializer(user).data, status=status.HTTP_200_OK)

#             # fallback if agent just returns text
#             return Response({"result": str(result)}, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




# ai_agents/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.utils import timezone
from django.db import transaction
from .models import ChatSession, ChatMessage
from .agent import get_agent_response
import logging
import time

logger = logging.getLogger(__name__)

class ChatSearchView(APIView):
    """
    Main chat endpoint for the AI search agent.
    Maintains conversation context and provides intelligent search responses.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        start_time = time.time()

        # Extract request data
        message = request.data.get("message", "").strip()
        session_id = request.data.get("session_id")
        search_type = request.data.get("search_type", "general")
        user_id = request.user.id if request.user.is_authenticated else None

        if not message:
            return Response(
                {"error": "No message provided"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                # Get or create chat session
                if session_id:
                    try:
                        session = ChatSession.objects.get(session_id=session_id)
                    except ChatSession.DoesNotExist:
                        session = ChatSession.objects.create(
                            session_id=session_id,
                            user_id=user_id
                        )
                else:
                    session = ChatSession.objects.create(user_id=user_id)
                    session_id = str(session.session_id)

                # Save user message
                user_message = ChatMessage.objects.create(
                    session=session,
                    role='user',
                    content=message,
                    search_type=search_type
                )

                # Get conversation history (last 10 messages for context)
                history = session.messages.order_by('timestamp')[:10]

                # Get AI response using the agent
                if search_type in ["database", "general"]:
                    from .sql_agent import process_database_question
                    response_content = process_database_question(message)
                else:
                    response_content = get_agent_response(
                        query=message,
                        conversation_history=history,
                        session_id=session_id
                    )

                # Save assistant response
                response_time = time.time() - start_time
                assistant_message = ChatMessage.objects.create(
                    session=session,
                    role='assistant',
                    content=response_content,
                    search_type=search_type,
                    response_time=response_time
                )

                # Update session metadata
                session.total_messages += 2  # User + assistant message
                session.last_activity = timezone.now()
                if not session.title:
                    session.title = message[:100]
                session.save()

                return Response({
                    "session_id": session_id,
                    "message": message,
                    "response": response_content,
                    "search_type": search_type,
                    "response_time": round(response_time, 2),
                    "message_count": session.total_messages,
                    "timestamp": assistant_message.timestamp.isoformat(),
                    "status": "success"
                }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Chat search error: {str(e)}")

            return Response({
                "error": f"Chat search failed: {str(e)}",
                "session_id": session_id,
                "message": message,
                "search_type": search_type,
                "status": "error"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChatHistoryView(APIView):
    """
    Get chat history for a session.
    """
    permission_classes = [AllowAny]

    def get(self, request, session_id=None):
        if not session_id:
            return Response(
                {"error": "Session ID required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            session = ChatSession.objects.get(session_id=session_id)
            messages = session.messages.order_by('timestamp')

            message_data = []
            for msg in messages:
                message_data.append({
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "search_type": msg.search_type,
                    "response_time": msg.response_time
                })

            return Response({
                "session_id": session_id,
                "title": session.title,
                "created_at": session.created_at.isoformat(),
                "total_messages": session.total_messages,
                "messages": message_data
            }, status=status.HTTP_200_OK)

        except ChatSession.DoesNotExist:
            return Response(
                {"error": "Session not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class UserSessionsView(APIView):
    """
    Get all chat sessions for a user.
    """
    def get(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        sessions = ChatSession.objects.filter(
            user=request.user,
            is_active=True
        ).order_by('-updated_at')[:50]  # Last 50 sessions

        session_data = []
        for session in sessions:
            session_data.append({
                "session_id": str(session.session_id),
                "title": session.title,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat(),
                "total_messages": session.total_messages,
                "last_activity": session.last_activity.isoformat()
            })

        return Response({
            "sessions": session_data,
            "total_count": len(session_data)
        }, status=status.HTTP_200_OK)


class SearchCapabilitiesView(APIView):
    """
    Get information about available search capabilities and chat features.
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        capabilities = {
            "chat_features": {
                "conversation_memory": "Maintains context across messages",
                "follow_up_questions": "Handles contextual follow-up queries",
                "session_management": "Persistent chat sessions",
                "search_suggestions": "Intelligent follow-up suggestions"
            },
            "search_types": {
                "general": "General web search for any topic",
                "news": "Recent news and current events",
                "research": "Academic and research information",
                "fact_check": "Fact-checking and verification",
                "conversational": "Context-aware search for follow-ups",
                "database": "Text-to-SQL RAG for querying internal data"
            },
            "available_tools": [
                "WebSearch - Real-time web search",
                "WikipediaSearch - Encyclopedia information",
                "ConversationalSearch - Context-aware search",
                "NewsSearch - Current news and events",
                "ResearchSearch - Academic information",
                "FactCheck - Statement verification",
                "FollowUpQuestions - Conversation continuations"
            ],
            "usage": {
                "start_chat": "POST /chat/ with {'message': 'your question'}",
                "continue_chat": "POST /chat/ with {'message': 'follow up', 'session_id': 'uuid'}",
                "get_history": "GET /chat/history/{session_id}/",
                "get_sessions": "GET /chat/sessions/"
            }
        }

        return Response(capabilities, status=status.HTTP_200_OK)
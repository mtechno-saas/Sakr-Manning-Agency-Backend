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
from .agent import agent
from .serializers import ShipSerializer, UserSerializer
from ships.models import Ship
from api.models import Users

class ShipAIView(APIView):
    """
    AI-powered ship and crew management.
    """

    def post(self, request, *args, **kwargs):
        query = request.data.get("query")
        if not query:
            return Response({"error": "No query provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # LangGraph agents use .invoke() instead of .run()
            result = agent.invoke({"messages": [("user", query)]})

            # The result may be text or a dict depending on tool return
            if isinstance(result, dict):
                if "ship_id" in result:
                    ship = Ship.objects.get(id=result["ship_id"])
                    return Response(ShipSerializer(ship).data, status=status.HTTP_200_OK)
                if "user_id" in result:
                    user = Users.objects.get(id=result["user_id"])
                    return Response(UserSerializer(user).data, status=status.HTTP_200_OK)

            return Response({"result": str(result)}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

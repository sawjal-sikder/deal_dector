from rest_framework.response import Response # type: ignore
from rest_framework.views import APIView # type: ignore
from rest_framework import generics # type: ignore
from celery.result import AsyncResult # type: ignore
from rest_framework import status # type: ignore
from .serializers import *
from .chat import let_chat
from .models import *


class ChatHistoryView(APIView):
    serializer_class = ChatHistorySerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data) 

        if serializer.is_valid():
            request_data = serializer.validated_data.get("request_data")

            # Start Celery task
            user_id = request.user.id
            task = let_chat.delay(request_data, user_id)


            return Response(
                {
                    "task_id": task.id,
                    "message": "Task started. Use task_id to fetch results.",
                },
                status=status.HTTP_202_ACCEPTED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChatResultView(APIView):
    """Fetch task result by task_id"""

    def get(self, request, task_id):
        result = AsyncResult(task_id)

        if result.ready():
            if result.successful():
                data = result.result

                if not isinstance(data, dict):
                    return Response(
                        {"status": "failed", "error": "Task returned no data."},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )

                # Update chat history with response if we can locate it
                chat_id = data.get("chat_id")
                if chat_id:
                    chat = ChatHistory.objects.filter(id=chat_id, user=request.user).first()
                else:
                    chat = ChatHistory.objects.filter(user=request.user).last()

                if chat:
                    chat.flag = data.get("flag") or chat.flag
                    if "response" in data:
                        chat.response_data = data.get("response")
                    chat.save()

                return Response({"status": "done", "result": data}, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"status": "failed", "error": str(result.result)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return Response({"status": "pending"}, status=status.HTTP_202_ACCEPTED)
    
    
    
class ChatHistoryListView(APIView):
    def get(self, request):
        chats = ChatHistory.objects.all()#.order_by('-created_at')
        serializer = ChatHistoryListSerializer(chats, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
  
class RecipeListView(APIView):
      def get(self, request):
          recipes = ChatHistory.objects.filter(user=request.user, flag="list_generated").order_by('-created_at')
          serializer = RecipeListSerializer(recipes, many=True)
          return Response(serializer.data, status=status.HTTP_200_OK)
      
      
class RecipeDetailView(generics.RetrieveAPIView):
    queryset = ChatHistory.objects.all()
    serializer_class = RecipeListSerializer
    lookup_field = "pk"

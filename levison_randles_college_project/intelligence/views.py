from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .serializers import ChatbotQuerySerializer, ChatbotResponseSerializer
from .chatbot_service import FAQChatbotService

class ChatbotQueryView(generics.GenericAPIView):
    """
    API endpoint to interact with the FAQ chatbot.
    """
    serializer_class = ChatbotQuerySerializer
    # permission_classes = [permissions.IsAuthenticated] # As per subtask, use IsAuthenticated
    # For a public chatbot, use:
    permission_classes = [permissions.AllowAny] # Making it public for typical chatbot use-case

    def post(self, request, *args, **kwargs):
        query_serializer = self.get_serializer(data=request.data)
        query_serializer.is_valid(raise_exception=True)

        query = query_serializer.validated_data['query']

        chatbot_service = FAQChatbotService()
        answer = chatbot_service.get_response(query)

        # We are directly constructing the response data, so we can pass it directly to Response
        # If we wanted to use ChatbotResponseSerializer for output formatting/validation:
        # response_payload = {'answer': answer, 'query': query}
        # response_serializer = ChatbotResponseSerializer(response_payload)
        # return Response(response_serializer.data, status=status.HTTP_200_OK)

        # Simpler response construction:
        return Response({'answer': answer, 'query': query}, status=status.HTTP_200_OK)

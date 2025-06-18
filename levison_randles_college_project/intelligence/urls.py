from django.urls import path
from .views import ChatbotQueryView

urlpatterns = [
    path('chatbot/query/', ChatbotQueryView.as_view(), name='chatbot_query'),
]

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatRoomViewSet, ChatMessageListView

router = DefaultRouter()
router.register(r'rooms', ChatRoomViewSet, basename='chatroom')

urlpatterns = [
    path('', include(router.urls)),
    # Path for listing messages for a specific chat room
    path('rooms/<str:room_id>/messages/', ChatMessageListView.as_view(), name='chatroom-messages-list'),
]

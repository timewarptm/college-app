from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Path for chat messaging for a specific room_id
    # Example: ws/chat/some-room-uuid/
    re_path(r'ws/chat/(?P<room_id>[^/]+)/$', consumers.MessagingConsumer.as_asgi()),
]

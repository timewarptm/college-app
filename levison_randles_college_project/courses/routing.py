from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Path for live signaling for a specific room_id
    # Example: ws/live/some-uuid-room-id/
    re_path(r'ws/live/(?P<room_id>[^/]+)/$', consumers.SignalingConsumer.as_asgi()),
]

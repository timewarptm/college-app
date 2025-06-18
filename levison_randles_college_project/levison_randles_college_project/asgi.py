import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import courses.routing
import messaging.routing # Import messaging routes

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'levison_randles_college_project.settings')

# Get the default Django ASGI application to handle HTTP requests
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            # Combine urlpatterns from different apps
            courses.routing.websocket_urlpatterns +
            messaging.routing.websocket_urlpatterns
        )
    ),
})

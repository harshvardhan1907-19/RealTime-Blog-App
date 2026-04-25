import os

from channels.routing import ProtocolTypeRouter, URLRouter
# ProtocolTypeRouter => Routes requests based on protocol (HTTP vs WebSocket)
# URLRouter =>	Routes WebSocket URLs to consumers (like urls.py for WebSockets)
from django.core.asgi import get_asgi_application
# get_asgi_application => Gets the standard Django ASGI application for HTTP
from channels.auth import AuthMiddlewareStack
# Purpose: Adds Django authentication to WebSocket connections
# Makes self.scope["user"] available in consumers
# Reads session cookies from browser
# Converts session to user object

import blogapp.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blogproject.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack( # Analogy:Security guard checking ID before allowing entry
        URLRouter(
            blogapp.routing.websocket_urlpatterns
        )
    ),
})


# Browser: ws://localhost:8000/ws/notifications/
#          ↓
# ProtocolTypeRouter: "This is WebSocket"
#          ↓
# Calls: AuthMiddlewareStack
#          ↓
# AuthMiddlewareStack: "Check user authentication"
#          ↓
# Calls: URLRouter
#          ↓
# URLRouter: "Find matching consumer"
#          ↓
# Calls: NotificationConsumer.connect()
#          ↓
# WebSocket connection established
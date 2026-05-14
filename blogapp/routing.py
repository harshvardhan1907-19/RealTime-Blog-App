from django.urls import path
from . import consumers

# Maps WebSocket URLs to consumers

websocket_urlpatterns = [
    path("ws/notifications/", consumers.NotificationConsumer.as_asgi()),
]
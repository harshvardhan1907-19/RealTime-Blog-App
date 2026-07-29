from channels.generic.websocket import AsyncWebsocketConsumer # Base class for WebSocket handlers (async version)
import json

# Handles WebSocket connections

class NotificationConsumer(AsyncWebsocketConsumer): # (gives WebSocket capabilities) 
    # Purposeb => Manages WebSocket connections for notifications
    async def connect(self):
        user = self.scope["user"]   # ✅ define first

        if user.is_anonymous:
            await self.close()
            return

        self.group_name = f"user_{user.id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
            # group_name = Which group to join
            # channel_name = Which specific connection to add // it work like post office
        )

        await self.accept()
        # Completes WebSocket handshake
        # Browser's socket.onopen fires

    async def disconnect(self, close_code):
        # close_code => Code explaining why connection closed (1000 = normal)
        if hasattr(self, "group_name"):   # ✅ safety check
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    # consumers.py - Add print in send_notification
    async def send_notification(self, event):
        # event => Dictionary containing notification data
        print(f"📨 Sending notification: {event.get('notification_id')}")
        await self.send(text_data=json.dumps({
            "type": "notification",
            "notification_id": event.get("notification_id"),
            "message": event["message"],
            "post_id": event.get("post_id"),
            "comment_id": event.get("comment_id"),
            "total_likes": event.get("total_likes"),
        }))

    # async def update_like_count(self, event):
    #     print(f"👍 Updating like count for Post {event.get('post_id')}: {event.get('new_count')}")
    #     await self.send(text_data = json.dumps({
    #         "type": "update_like_count",
    #         "post_id": event.get("post_id"),
    #         "new_count": event.get("new_count"),
    #     }))
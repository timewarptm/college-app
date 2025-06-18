import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .models import ChatRoom, ChatMessage
from .serializers import ChatMessageSerializer # To serialize messages for broadcast
from django.utils import timezone

class MessagingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get('user', AnonymousUser())
        self.room_id = self.scope['url_route']['kwargs'].get('room_id')

        if not self.user.is_authenticated or not self.room_id:
            await self.close()
            return

        self.room_group_name = f'chat_{self.room_id}'

        is_participant, room = await self.check_participation(self.user, self.room_id)
        if not is_participant:
            await self.close()
            return

        self.room = room # Store room object for later use

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        print(f"User {self.user} connected to chat room {self.room_id}")

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
            print(f"User {self.user} disconnected from chat room {self.room_id}")

    async def receive(self, text_data):
        if not self.user.is_authenticated: # Should be caught by connect, but as a safeguard
            return

        try:
            data = json.loads(text_data)
            message_content = data.get('message')
            if not message_content:
                return # Or send error back to client
        except json.JSONDecodeError:
            return # Or send error

        # Create and save ChatMessage instance
        chat_message = await self.save_chat_message(self.user, self.room, message_content)

        # Serialize the message
        # Need to pass context for UserSerializer if it's used (e.g. for sender_details)
        # However, ChatMessageSerializer is simple enough here.
        # For complex serializers, you might need to build context:
        # serializer_context = {'request': self.scope} # self.scope might not be a full request
        serialized_message = ChatMessageSerializer(chat_message).data
        # Ensure timestamp is ISO format for JS if not already
        serialized_message['timestamp'] = chat_message.timestamp.isoformat()


        # Broadcast the message to the room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message_broadcast', # Method name to handle the message
                'message': serialized_message
            }
        )

    async def chat_message_broadcast(self, event):
        """Sends a message to the WebSocket client (part of the group)."""
        message = event['message']
        await self.send(text_data=json.dumps(message))

    @database_sync_to_async
    def check_participation(self, user, room_id):
        try:
            room = ChatRoom.objects.get(id=room_id)
            if room.participants.filter(pk=user.pk).exists():
                return True, room
        except ChatRoom.DoesNotExist:
            pass
        return False, None

    @database_sync_to_async
    def save_chat_message(self, user, room, content):
        return ChatMessage.objects.create(sender=user, room=room, content=content)

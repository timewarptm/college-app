import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser # For type hinting if user is not authenticated
from .models import LiveSession, Enrollment # Import necessary models

class SignalingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get('user', AnonymousUser()) # Get user from scope (AuthMiddlewareStack)
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'live_session_{self.room_id}'

        if not self.user.is_authenticated:
            print(f"Connection attempt by unauthenticated user to room {self.room_id}. Closing.")
            await self.close()
            return

        allowed, live_session = await self.check_user_authorization(self.user, self.room_id)

        if not allowed:
            print(f"User {self.user} not authorized for room {self.room_id}. Closing connection.")
            await self.close()
            return

        # Store live_session on self if needed for other methods, e.g. status checks
        self.live_session = live_session

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        print(f"User {self.user} connected to room {self.room_id} (LiveSession status: {self.live_session.status}), group {self.room_group_name}")

    @database_sync_to_async
    def check_user_authorization(self, user, room_id):
        try:
            live_session = LiveSession.objects.select_related('course').get(room_id=room_id)
        except LiveSession.DoesNotExist:
            print(f"LiveSession with room_id {room_id} does not exist.")
            return False, None

        # Teachers can connect to their 'pending' or 'live' sessions.
        if user.role == 'teacher':
            if live_session.created_by == user:
                if live_session.status in ['pending', 'live']:
                    return True, live_session
                else:
                    print(f"Teacher {user} attempting to connect to their session {room_id} but status is '{live_session.status}'.")
                    return False, live_session
            else: # Teacher trying to access a session not created by them
                print(f"Teacher {user} is not the creator of session {room_id}.")
                return False, live_session

        # Students can only connect to 'live' sessions for courses they are enrolled in.
        elif user.role == 'student':
            if live_session.status != 'live':
                print(f"Student {user} attempting to connect to session {room_id} but status is '{live_session.status}'.")
                return False, live_session

            is_enrolled = Enrollment.objects.filter(student=user, course=live_session.course).exists()
            if not is_enrolled:
                print(f"Student {user} is not enrolled in course {live_session.course} for session {room_id}.")
                return False, live_session
            return True, live_session

        else: # Other roles or unauthenticated (already handled but good for clarity)
            print(f"User {user} with role {user.role} not authorized for session {room_id}.")
            return False, live_session

    async def disconnect(self, close_code):
        # Leave room group
        if hasattr(self, 'room_group_name'): # Ensure room_group_name was set
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            print(f"User {self.scope.get('user')} disconnected from room {self.room_id}")

    async def receive(self, text_data):
        """
        Receive message from WebSocket.
        Echoes the message back to the sender or broadcasts to the group.
        This is a basic example for signaling. WebRTC signaling messages
        would be passed through here.
        """
        print(f"Received message in room {self.room_id} from {self.scope.get('user')}: {text_data}")
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')

        # For WebRTC, messages might be offers, answers, candidates, etc.
        # The consumer would broadcast these to other users in the same room.
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'broadcast_message', # This corresponds to a method name in this consumer
                'message': text_data_json,
                'sender_channel_name': self.channel_name # To avoid sending message back to sender if not desired
            }
        )

    async def broadcast_message(self, event):
        """
        Handles messages sent to the group.
        Sends the message to the WebSocket client.
        """
        message = event['message']
        sender_channel_name = event.get('sender_channel_name')

        # Optionally, don't send the message back to the original sender
        if self.channel_name != sender_channel_name:
            await self.send(text_data=json.dumps(message))
            print(f"Sent message to {self.scope.get('user')} in group {self.room_group_name}: {message}")
        else:
            print(f"Sender {self.scope.get('user')} is self, not sending broadcast message back.")

    # Example of an async database check (needs @database_sync_to_async decorator for ORM calls)
    # @database_sync_to_async # This was the old example method
    # def is_user_allowed(self, user, room_id):
    # ... (previous example content) ...

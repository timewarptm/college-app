from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ChatRoom, ChatMessage
from accounts.serializers import UserSerializer # Assuming UserSerializer is in accounts.serializers

User = get_user_model()

class ChatMessageSerializer(serializers.ModelSerializer):
    sender_details = UserSerializer(source='sender', read_only=True)

    class Meta:
        model = ChatMessage
        fields = ('id', 'room', 'sender', 'sender_details', 'content', 'timestamp')
        read_only_fields = ('id', 'timestamp', 'sender_details')
        # 'sender' will be set from request.user in the view/consumer for new messages.
        # 'room' will be from URL context or validated data.

    def create(self, validated_data):
        # Ensure sender is set from context if not provided (e.g. from WebSocket consumer)
        if 'sender' not in validated_data and 'request' in self.context:
            validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)


class ChatRoomSerializer(serializers.ModelSerializer):
    participant_details = UserSerializer(source='participants', many=True, read_only=True)
    # `participants` field (default M2M PrimaryKeyRelatedField) is used for write operations (list of user IDs).

    last_message = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ChatRoom
        fields = (
            'id', 'name', 'room_type',
            'participants', 'participant_details',
            'created_at', 'updated_at', 'last_message_at', 'last_message'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'last_message_at', 'participant_details', 'last_message')

    def get_last_message(self, obj):
        """Returns the last message of the chat room."""
        last_msg = obj.messages.order_by('-timestamp').first()
        if last_msg:
            # Can return a simplified representation or the full ChatMessageSerializer
            return ChatMessageSerializer(last_msg, context=self.context).data
        return None

    def validate_participants(self, value):
        if not value: # Ensure participants list is not empty
            raise serializers.ValidationError("A chat room must have at least one participant.")
        # Further validation for DM rooms (e.g. max 2 participants) can be done in validate method or view.
        return value

    def validate(self, data):
        room_type = data.get('room_type', self.instance.room_type if self.instance else 'dm')
        participants = data.get('participants') # This will be a list of User objects after initial validation
        name = data.get('name')

        if room_type == 'dm':
            if name: # DM rooms should not have a name set by user
                raise serializers.ValidationError({"name": "Direct message rooms should not have a custom name."})
            if participants and len(participants) > 2:
                raise serializers.ValidationError({"participants": "Direct messages can only have up to two participants."})
        elif room_type == 'group':
            if not name:
                raise serializers.ValidationError({"name": "Group chats must have a name."})
        return data

    def create(self, validated_data):
        # Add the creating user to participants if not already included by client
        user = self.context['request'].user
        participants = validated_data.get('participants', [])
        if user not in participants:
            participants.append(user)
        validated_data['participants'] = participants

        # For DM rooms, ensure there's exactly two participants if client only sends one other.
        # Or, if client sends one participant (the other user), add current user.
        room_type = validated_data.get('room_type')
        if room_type == 'dm':
            if len(participants) == 1 and user != participants[0]: # Client sent the other user
                participants.append(user)
            elif len(participants) == 0: # Should not happen if validation is good, but as safeguard
                 participants.append(user) # DM with self? Or require other participant?
                 # This scenario (DM with self) might need specific handling or be disallowed.
                 # For now, it implies creating a room with just the user.

            # Ensure unique DM room for a pair of users (if that's a requirement)
            # This can be complex. One way is to create a canonical representation of the pair
            # and check if a room with that pair already exists. This is often handled in the view.

        return super().create(validated_data)

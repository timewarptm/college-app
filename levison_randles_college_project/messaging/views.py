from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from django.db.models import Q, Prefetch
from django.shortcuts import get_object_or_404
from .models import ChatRoom, ChatMessage
from .serializers import ChatRoomSerializer, ChatMessageSerializer
from .permissions import IsRoomParticipantPermission # Will create this next

class ChatRoomViewSet(viewsets.ModelViewSet):
    """
    API endpoint for chat rooms.
    Users can only see and interact with rooms they are participants in.
    """
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated] # Base permission

    def get_queryset(self):
        # Users can only list rooms they are a participant in.
        # Prefetch related participants and the last message for optimization.
        # Note: Fetching last message here can be N+1 if not careful.
        # The serializer method `get_last_message` handles fetching it.
        return self.request.user.chat_rooms.all().prefetch_related(
            Prefetch('participants', queryset=get_user_model().objects.only('id', 'email', 'first_name', 'last_name', 'role'))
        ).order_by('-last_message_at')


    def perform_create(self, serializer):
        # The creating user is automatically added to participants in the serializer's create method.
        # Room type and participant validation is largely handled in the serializer.
        # Ensure the serializer has access to the request context for the user.
        serializer.save()

    def get_permissions(self):
        # Apply IsRoomParticipantPermission for object-level actions
        if self.action in ['retrieve', 'update', 'partial_update', 'destroy', 'add_participant', 'remove_participant']:
            return [permissions.IsAuthenticated(), IsRoomParticipantPermission()]
        return super().get_permissions()

    # Example custom actions for managing participants (could be added)
    # @action(detail=True, methods=['post'], url_path='add-participant')
    # def add_participant(self, request, pk=None):
    #     room = self.get_object() # IsRoomParticipantPermission has run
    #     user_id_to_add = request.data.get('user_id')
    #     # Add logic: only admin of group chat or specific conditions
    #     ...

    # @action(detail=True, methods=['post'], url_path='remove-participant')
    # def remove_participant(self, request, pk=None):
    #     room = self.get_object()
    #     user_id_to_remove = request.data.get('user_id')
    #     # Add logic: only admin of group chat or self-removal
    #     ...

class ChatMessageListView(generics.ListAPIView):
    """
    API endpoint to list messages for a specific chat room.
    POSTing new messages is primarily handled by WebSockets.
    """
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated] # View-level permission

    def get_permissions(self):
        # For object-level permission (i.e., checking if user can access this specific room's messages)
        # We need to fetch the room and then check.
        if self.request.method == 'GET': # Only for GET as it's ListAPIView
             # We create an instance of IsRoomParticipantPermission to call its has_object_permission
            room_permission = IsRoomParticipantPermission()
            room_id = self.kwargs.get('room_id')
            room = get_object_or_404(ChatRoom, pk=room_id)
            if not room_permission.has_object_permission(self.request, self, room):
                self.permission_denied(
                    self.request, message=getattr(room_permission, 'message', None)
                )
        return super().get_permissions()


    def get_queryset(self):
        room_id = self.kwargs['room_id']
        # Permission check (done in get_permissions) ensures user is part of this room.
        return ChatMessage.objects.filter(room_id=room_id).order_by('timestamp').select_related('sender')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['room_id'] = self.kwargs.get('room_id')
        return context

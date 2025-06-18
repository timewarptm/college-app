from rest_framework.permissions import BasePermission
from .models import ChatRoom

class IsRoomParticipantPermission(BasePermission):
    """
    Allows access only to users who are participants of the chat room.
    """
    message = "You are not a participant of this chat room."

    def has_object_permission(self, request, view, obj):
        # obj is expected to be a ChatRoom instance.
        if not request.user.is_authenticated:
            return False
        if isinstance(obj, ChatRoom):
            return obj.participants.filter(pk=request.user.pk).exists()
        return False

    # If used for view-level permission where object is not yet fetched,
    # this might need adaptation or be used in conjunction with other checks.
    # For instance, in ChatMessageListView, we fetch the room in get_permissions.
    def has_permission(self, request, view):
        # This can be used for view-level checks if the view is tied to a room_id in URL
        # and we fetch the room to check participation.
        # However, for ModelViewSet, it's typically has_object_permission that's key for detail routes.
        # For list routes, queryset is filtered. For create, other logic applies.
        return request.user.is_authenticated
        # The actual check if user can access a list of messages for a *specific room*
        # is handled in ChatMessageListView.get_permissions by fetching the room.

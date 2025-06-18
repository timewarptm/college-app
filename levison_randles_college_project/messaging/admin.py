from django.contrib import admin
from .models import ChatRoom, ChatMessage

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'room_type', 'created_at', 'updated_at', 'last_message_at', 'participant_count')
    list_filter = ('room_type', 'created_at', 'last_message_at')
    search_fields = ('name', 'participants__email', 'participants__first_name')
    filter_horizontal = ('participants',) # Easier to manage M2M for participants

    def participant_count(self, obj):
        return obj.participants.count()
    participant_count.short_description = "Participants"

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'room_summary', 'sender_summary', 'content_preview', 'timestamp')
    list_filter = ('timestamp', 'room__id', 'sender') # Filter by room ID or sender
    search_fields = ('content', 'sender__email', 'room__name') # Search message content, sender email, or room name
    raw_id_fields = ('room', 'sender') # Useful for performance with many rooms/users
    date_hierarchy = 'timestamp'

    def room_summary(self, obj):
        return str(obj.room) # Uses ChatRoom.__str__
    room_summary.short_description = "Room"

    def sender_summary(self, obj):
        return obj.sender.get_full_name() or obj.sender.email
    sender_summary.short_description = "Sender"

    def content_preview(self, obj):
        return (obj.content[:50] + '...') if len(obj.content) > 50 else obj.content
    content_preview.short_description = "Preview"

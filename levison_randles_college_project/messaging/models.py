from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.db.models import Max

class ChatRoom(models.Model):
    ROOM_TYPE_CHOICES = [
        ('dm', _('Direct Message')),
        ('group', _('Group Chat')),
    ]

    name = models.CharField(
        _("name"),
        max_length=100,
        null=True,
        blank=True,
        help_text=_("Name of the group chat. Not used for DMs.")
    )
    room_type = models.CharField(
        _("room type"),
        max_length=10,
        choices=ROOM_TYPE_CHOICES,
        default='dm'
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='chat_rooms',
        help_text=_("Users participating in this chat room.")
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)
    last_message_at = models.DateTimeField(
        _("last message at"),
        null=True,
        blank=True,
        help_text=_("Timestamp of the last message, for sorting rooms.")
    )

    def __str__(self):
        if self.room_type == 'group' and self.name:
            return self.name
        elif self.room_type == 'dm':
            user_names = ", ".join([user.get_full_name() or user.email for user in self.participants.all()[:2]])
            # Check if participants are loaded, might need prefetch_related for efficiency in some contexts
            # For __str__ it's usually fine for admin, but be wary in high-volume serialization.
            return f"DM with {user_names}" if user_names else f"DM Room {self.id}"
        return f"Room {self.id} ({self.room_type})"


    def update_last_message_at(self, timestamp=None):
        """
        Updates the last_message_at field.
        If timestamp is provided, use it. Otherwise, query the latest message.
        """
        if timestamp:
            self.last_message_at = timestamp
        else:
            latest_message_timestamp = self.messages.aggregate(latest_ts=Max('timestamp'))['latest_ts']
            if latest_message_timestamp:
                self.last_message_at = latest_message_timestamp

        if self.last_message_at: # Ensure there's a value to save
             self.save(update_fields=['last_message_at'])


    class Meta:
        verbose_name = _("Chat Room")
        verbose_name_plural = _("Chat Rooms")
        ordering = ['-last_message_at', '-updated_at']


class ChatMessage(models.Model):
    room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='messages',
        help_text=_("The chat room this message belongs to.")
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, # Or models.SET_NULL if messages should persist if sender is deleted
        related_name='sent_messages',
        help_text=_("The user who sent this message.")
    )
    content = models.TextField(_("content"))
    timestamp = models.DateTimeField(_("timestamp"), auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender} in {self.room.id} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new: # Only update room's timestamp if it's a new message
            self.room.update_last_message_at(timestamp=self.timestamp)

    class Meta:
        verbose_name = _("Chat Message")
        verbose_name_plural = _("Chat Messages")
        ordering = ['timestamp']

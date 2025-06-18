from rest_framework import serializers
from django.contrib.auth import get_user_model
from decimal import Decimal
from .models import Tip # Assuming Tip model is in the same app
from accounts.serializers import UserSerializer # For TipDetailSerializer

User = get_user_model()

class TipCreateSerializer(serializers.Serializer):
    tippee_id = serializers.IntegerField(
        help_text="The ID of the user to receive the tip."
    )
    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0.01'),
        help_text="Amount of the tip. Must be positive."
    )
    message = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500,
        help_text="Optional message to send with the tip."
    )

    def validate_tippee_id(self, value):
        """
        Check if the tippee exists and is not the current user.
        """
        request_user = self.context['request'].user
        if value == request_user.id:
            raise serializers.ValidationError("You cannot tip yourself.")
        try:
            User.objects.get(pk=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("The user you are trying to tip does not exist.")
        return value

    def validate_amount(self, value):
        """
        Ensure amount is positive (already handled by min_value, but good for explicit check).
        Additional checks like max tip amount could be added here.
        """
        if value <= Decimal('0.00'): # min_value in field definition handles this, but explicit is fine.
            raise serializers.ValidationError("Tip amount must be a positive value.")
        return value

    # General validation for checking tipper's balance would ideally be in the view
    # during the transaction, as it requires locking the user row.
    # However, a preliminary check could be done here if desired, but it might not be transaction-safe.


class TipDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying Tip details, including nested tipper and tippee info.
    """
    tipper = UserSerializer(read_only=True)
    tippee = UserSerializer(read_only=True)

    class Meta:
        model = Tip
        fields = ('id', 'tipper', 'tippee', 'amount', 'timestamp', 'message')
        read_only_fields = fields # All fields are read-only for detail display via this serializer

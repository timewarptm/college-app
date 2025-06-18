from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
from django.core.exceptions import ValidationError # Import ValidationError for clean method

class Tip(models.Model):
    tipper = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='tips_given',
        on_delete=models.CASCADE, # Or models.SET_NULL if you want to keep tip records if a user is deleted
        help_text=_("The user who gave the tip.")
    )
    tippee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='tips_received',
        on_delete=models.CASCADE, # Or models.SET_NULL
        help_text=_("The user who received the tip.")
    )
    amount = models.DecimalField(
        _("amount"),
        max_digits=10,
        decimal_places=2,
        help_text=_("Amount of the tip.")
    )
    timestamp = models.DateTimeField(_("timestamp"), auto_now_add=True)
    message = models.TextField(
        _("message"),
        blank=True,
        null=True,
        help_text=_("Optional message sent with the tip.")
    )

    def __str__(self):
        # It's good practice to ensure tipper and tippee are not None if using SET_NULL
        tipper_str = str(self.tipper) if self.tipper else "Unknown Tipper"
        tippee_str = str(self.tippee) if self.tippee else "Unknown Tippee"
        return f"Tip from {tipper_str} to {tippee_str} of {self.amount}"

    class Meta:
        verbose_name = _("Tip")
        verbose_name_plural = _("Tips")
        ordering = ['-timestamp']

    def clean(self):
        """
        Custom validation for the Tip model.
        """
        super().clean() # Call parent's clean method
        if self.tipper and self.tippee and self.tipper == self.tippee:
            raise ValidationError({'tipper': _("Tipper and tippee cannot be the same user."),
                                   'tippee': _("Tipper and tippee cannot be the same user.")})
        if self.amount is not None and self.amount <= Decimal('0.00'):
            raise ValidationError({'amount': _("Tip amount must be positive.")})


from store.models import Product # Import Product model

class PurchaseOrder(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending', _('Pending')),          # Order created, awaiting payment or processing
        ('processing', _('Processing')),    # Payment received, order is being processed (e.g., for digital goods access)
        ('completed', _('Completed')),      # Order fulfilled
        ('failed', _('Failed')),            # Payment failed or other failure
        ('refunded', _('Refunded')),        # Order was refunded
        ('cancelled', _('Cancelled')),      # Order was cancelled by user or system before completion
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='purchase_orders',
        on_delete=models.SET_NULL, # Keep order history even if user is deleted
        null=True,
        blank=True, # Can be blank if, for example, system creates an order or guest checkout
        help_text=_("User who made the purchase. Null if user is deleted or guest checkout.")
    )
    product = models.ForeignKey(
        Product, # Corrected from 'store.Product' to just Product as it's imported
        related_name='purchase_orders',
        on_delete=models.PROTECT, # Prevent product deletion if orders exist
        help_text=_("The product purchased.")
    )
    quantity = models.PositiveIntegerField(_("quantity"), default=1)
    unit_price = models.DecimalField(
        _("unit price"),
        max_digits=10,
        decimal_places=2,
        help_text=_("Price of one unit of the product at the time of purchase.")
    )
    total_amount = models.DecimalField(
        _("total amount"),
        max_digits=12,
        decimal_places=2,
        help_text=_("Total amount for this order (quantity * unit_price). Will be auto-calculated if not provided.")
    )
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default='pending'
    )
    transaction_id = models.CharField(
        _("transaction ID"),
        max_length=255,
        blank=True,
        null=True,
        unique=True, # Assuming one order per external transaction_id if provided
        db_index=True,
        help_text=_("External transaction ID from payment provider or internal unique ID for the transaction event.")
    )
    payment_method_details = models.JSONField(
        _("payment method details"),
        blank=True,
        null=True,
        help_text=_("Details about the payment method used, e.g., 'paid_with_internal_balance', simulated Stripe charge ID.")
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    def __str__(self):
        user_str = str(self.user) if self.user else "Guest/System"
        product_name = self.product.name if self.product else "N/A"
        return f"Order {self.id} by {user_str} for {self.quantity}x {product_name} ({self.status})"

    def save(self, *args, **kwargs):
        if self.unit_price is not None and self.quantity is not None:
            self.total_amount = self.unit_price * self.quantity
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        if self.quantity <= 0:
            raise ValidationError({'quantity': _("Quantity must be positive.")})
        if self.unit_price < Decimal('0.00'): # Allow 0 for free items, but not negative
            raise ValidationError({'unit_price': _("Unit price cannot be negative.")})
        # total_amount is calculated in save, but if provided, ensure it matches
        if self.total_amount is not None and self.unit_price is not None and self.quantity is not None:
            if self.total_amount != (self.unit_price * self.quantity):
                raise ValidationError(_("Total amount does not match unit price times quantity."))


    class Meta:
        verbose_name = _("Purchase Order")
        verbose_name_plural = _("Purchase Orders")
        ordering = ['-created_at']

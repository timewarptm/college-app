from django.db import models
from django.utils.translation import gettext_lazy as _
from decimal import Decimal, InvalidOperation # Import InvalidOperation
from django.core.exceptions import ValidationError

class Product(models.Model):
    PRODUCT_ITEM_TYPES = [
        ('digital_good', _('Digital Good')),
        ('service_booking', _('Service Booking')),
        ('event_ticket', _('Event Ticket')),
        ('course_material_access', _('Course Material Access')),
        ('question_allowance', _('Question Allowance')), # E.g., for FAQ chatbot or teacher questions
        ('internal_credit_purchase', _('Internal Credit Purchase')), # For buying site currency/balance
    ]

    name = models.CharField(_("name"), max_length=255)
    description = models.TextField(_("description"))
    price = models.DecimalField(
        _("price"),
        max_digits=10,
        decimal_places=2
    )
    item_type = models.CharField(
        _("item type"),
        max_length=50,
        choices=PRODUCT_ITEM_TYPES
    )
    is_active = models.BooleanField(
        _("is active"),
        default=True,
        help_text=_("Is this product currently available for purchase?")
    )
    stock_quantity = models.IntegerField(
        _("stock quantity"),
        null=True,
        blank=True,
        help_text=_("For items with limited availability like tickets. Null means unlimited.")
    )
    # meta_data can store things like:
    # - For 'course_material_access': {'course_id': 123}
    # - For 'event_ticket': {'event_id': 456, 'ticket_type': 'VIP'}
    # - For 'question_allowance': {'count': 10}
    # - For 'internal_credit_purchase': {'credit_amount': 100.00}
    meta_data = models.JSONField(
        _("meta data"),
        null=True,
        blank=True,
        help_text=_("To store item_type specific data, e.g., course_id, event_id, credit_amount.")
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        if self.price is not None and self.price < Decimal('0.00'): # Price should not be negative
            raise ValidationError({'price': _("Price cannot be negative.")})

        if self.stock_quantity is not None and self.stock_quantity < 0:
            raise ValidationError({'stock_quantity': _("Stock quantity cannot be negative.")})

        # Validation for meta_data based on item_type
        if self.item_type == 'internal_credit_purchase':
            if not isinstance(self.meta_data, dict) or 'credit_amount' not in self.meta_data:
                raise ValidationError({'meta_data': _("For 'Internal Credit Purchase', meta_data must contain 'credit_amount'.")})
            try:
                credit_val = Decimal(str(self.meta_data['credit_amount'])) # Ensure it's processed as string for Decimal
                if credit_val <= Decimal('0.00'):
                    raise ValidationError({'meta_data': _("'credit_amount' must be positive.")})
            except (TypeError, ValueError, InvalidOperation):
                 raise ValidationError({'meta_data': _("'credit_amount' must be a valid decimal number.")})

        elif self.item_type == 'question_allowance':
            if not isinstance(self.meta_data, dict) or 'count' not in self.meta_data:
                raise ValidationError({'meta_data': _("For 'Question Allowance', meta_data must contain 'count'.")})
            try:
                count_val = int(self.meta_data['count'])
                if count_val <=0:
                    raise ValidationError({'meta_data': _("'count' must be a positive integer.")})
            except (TypeError, ValueError):
                 raise ValidationError({'meta_data': _("'count' must be a valid integer.")})

        # Add more meta_data validation for other types as needed (e.g., course_id existence)
        # Example for 'course_material_access':
        # elif self.item_type == 'course_material_access':
        #     if not isinstance(self.meta_data, dict) or 'course_id' not in self.meta_data:
        #         raise ValidationError({'meta_data': _("For 'Course Material Access', meta_data must contain 'course_id'.")})
        #     if not isinstance(self.meta_data.get('course_id'), int): # Or check if course exists
        #         raise ValidationError({'meta_data': _("'course_id' must be a valid integer ID.")})


    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        ordering = ['name']

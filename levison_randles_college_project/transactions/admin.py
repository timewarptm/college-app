from django.contrib import admin
from .models import Tip, PurchaseOrder

@admin.register(Tip)
class TipAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipper_email', 'tippee_email', 'amount', 'timestamp', 'message_preview')
    list_filter = ('timestamp', 'amount')
    search_fields = (
        'tipper__email', 'tipper__first_name', 'tipper__last_name',
        'tippee__email', 'tippee__first_name', 'tippee__last_name',
        'message'
    )
    raw_id_fields = ('tipper', 'tippee') # Useful for ForeignKey fields with many users
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)

    def tipper_email(self, obj):
        return obj.tipper.email if obj.tipper else None
    tipper_email.short_description = "Tipper's Email"
    tipper_email.admin_order_field = 'tipper__email'


    def tippee_email(self, obj):
        return obj.tippee.email if obj.tippee else None
    tippee_email.short_description = "Tippee's Email"
    tippee_email.admin_order_field = 'tippee__email'

    def message_preview(self, obj):
        if obj.message:
            return (obj.message[:50] + '...') if len(obj.message) > 50 else obj.message
        return "-"
    message_preview.short_description = "Message Preview"

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_email', 'product_name', 'quantity', 'total_amount', 'status', 'transaction_id_display', 'created_at')
    list_filter = ('status', 'product', 'created_at')
    search_fields = ('user__email', 'product__name', 'transaction_id', 'id')
    raw_id_fields = ('user', 'product')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    readonly_fields = ('created_at', 'updated_at', 'total_amount') # As total_amount is auto-calculated

    fieldsets = (
        (None, {
            'fields': ('user', 'product', 'status', 'transaction_id')
        }),
        ('Order Details', {
            'fields': ('quantity', 'unit_price', 'total_amount')
        }),
        ('Payment Information', {
            'fields': ('payment_method_details',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def user_email(self, obj):
        return obj.user.email if obj.user else "Guest/System"
    user_email.short_description = "User Email"
    user_email.admin_order_field = 'user__email'

    def product_name(self, obj):
        return obj.product.name if obj.product else "N/A"
    product_name.short_description = "Product"
    product_name.admin_order_field = 'product__name'

    def transaction_id_display(self, obj):
        return obj.transaction_id if obj.transaction_id else "-"
    transaction_id_display.short_description = "Transaction ID"

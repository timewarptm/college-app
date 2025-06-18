from django.contrib import admin
from .models import Product
import json # For pretty printing JSON in admin if needed

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'item_type', 'price', 'is_active', 'stock_quantity_display', 'created_at')
    list_filter = ('item_type', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'item_type', 'meta_data__icontains') # Search in JSON field
    ordering = ('name',)

    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'item_type', 'price', 'is_active')
        }),
        ('Stock & Meta Data', {
            'fields': ('stock_quantity', 'meta_data'),
            'classes': ('collapse',), # Collapsible section
        }),
    )

    def stock_quantity_display(self, obj):
        if obj.stock_quantity is None:
            return "Unlimited"
        return obj.stock_quantity
    stock_quantity_display.short_description = "Stock"

    # Optionally, to pretty print JSONField in admin (requires Django 3.1+)
    # This is more for readonly display in admin; editing JSON is usually direct.
    # def display_meta_data(self, obj):
    #     if obj.meta_data:
    #         return json.dumps(obj.meta_data, indent=4)
    #     return "-"
    # display_meta_data.short_description = "Meta Data (Formatted)"
    # readonly_fields = ('display_meta_data',) # If you add the above method

    def get_queryset(self, request):
        # Optimize by prefetching related data if any ForeignKeys were present
        return super().get_queryset(request)

    # Add validation or custom forms here if meta_data needs more structured input in admin
    # For example, based on item_type, you might want different form fields for meta_data.
    # This would involve overriding get_form method.

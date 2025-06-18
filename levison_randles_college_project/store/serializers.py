from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    availability = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'description',
            'price',
            'item_type',
            'stock_quantity', # Keep original stock_quantity for info if needed by admin/internal
            'availability',   # More user-friendly availability status
            'meta_data',
            'is_active', # Useful for client to know, though list view filters by it
            'created_at',
            'updated_at'
        )
        read_only_fields = ( # For a listing API, all are effectively read-only by this view.
            'id', 'name', 'description', 'price', 'item_type',
            'stock_quantity', 'availability', 'meta_data', 'is_active',
            'created_at', 'updated_at'
        )

    def get_availability(self, obj):
        if obj.stock_quantity is None:
            return "Unlimited"
        elif obj.stock_quantity > 0:
            return "In Stock"
        else:
            return "Out of Stock"

    # If stock_quantity should not be exposed directly to clients, remove it from 'fields'
    # and rely solely on 'availability'. For now, keeping it for completeness.
    # If meta_data contains sensitive info, consider a custom representation or exclude it.

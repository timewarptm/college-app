from rest_framework import generics, permissions
from .models import Product
from .serializers import ProductSerializer
# For filtering, if added later:
# from django_filters.rest_framework import DjangoFilterBackend
# from rest_framework import filters

class ProductListView(generics.ListAPIView):
    """
    API endpoint to list all active, purchasable products.
    """
    queryset = Product.objects.filter(is_active=True).order_by('name')
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny] # Products are publicly viewable

    # Optional: Add filtering backends if more complex filtering is needed later
    # filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    # filterset_fields = ['item_type'] # Example if Product model had more filterable direct fields
    # search_fields = ['name', 'description', 'meta_data__icontains'] # Search in name, desc, and JSON
    # ordering_fields = ['price', 'name', 'created_at']
    # ordering = ['name'] # Default ordering (already in queryset)

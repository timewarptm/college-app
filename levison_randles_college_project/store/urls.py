from django.urls import path
from .views import ProductListView

urlpatterns = [
    path('products/', ProductListView.as_view(), name='product-list'),
    # Future: Add endpoint for product detail if needed
    # path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
]

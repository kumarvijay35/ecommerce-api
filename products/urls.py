from django.urls import path
from .views import (
    CategoryListCreateView,
    ProductListCreateView,
    ProductDetailView,
    MyProductsView,
)

urlpatterns = [
    path('categories/', CategoryListCreateView.as_view(), name='categories'),
    path('', ProductListCreateView.as_view(), name='product-list'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('my-products/', MyProductsView.as_view(), name='my-products'),
]
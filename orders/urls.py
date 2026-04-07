from django.urls import path
from .views import (
    CartView,
    PlaceOrderView,
    VerifyPaymentView,
    MyOrdersView,
    OrderDetailView,
)

urlpatterns = [
    path('cart/', CartView.as_view(), name='cart'),
    path('place-order/', PlaceOrderView.as_view(), name='place-order'),
    path('verify-payment/', VerifyPaymentView.as_view(), name='verify-payment'),
    path('my-orders/', MyOrdersView.as_view(), name='my-orders'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
]
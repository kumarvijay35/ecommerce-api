
# Register your models here.
from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem

admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Cart)
admin.site.register(CartItem)
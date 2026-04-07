import razorpay
import hmac
import hashlib

from django.conf import settings
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Cart, CartItem, Order, OrderItem
from .serializers import CartSerializer, OrderSerializer
from products.models import Product

# Razorpay client
razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)


class CartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def post(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=404)

        if product.stock < quantity:
            return Response({'error': 'Not enough stock'}, status=400)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()

        return Response(CartSerializer(cart).data, status=201)

    def delete(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        item_id = request.data.get('item_id')
        try:
            item = CartItem.objects.get(id=item_id, cart=cart)
            item.delete()
        except CartItem.DoesNotExist:
            return Response({'error': 'Item not found'}, status=404)
        return Response(CartSerializer(cart).data)


class PlaceOrderView(APIView):
    """
    Creates order in our DB + creates Razorpay order.
    Returns razorpay_order_id for frontend to trigger payment.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        items = cart.items.all()

        if not items.exists():
            return Response({'error': 'Cart is empty'}, status=400)

        shipping_address = request.data.get('shipping_address', '')
        if not shipping_address:
            return Response({'error': 'Shipping address is required'}, status=400)

        total = cart.get_total()

        # Create Razorpay order (amount in paise)
        razorpay_order = razorpay_client.order.create({
            'amount': int(total * 100),  # convert ₹ to paise
            'currency': 'INR',
            'payment_capture': 1,        # auto capture payment
        })

        # Create order in our DB
        order = Order.objects.create(
            user=request.user,
            total_price=total,
            shipping_address=shipping_address,
            razorpay_order_id=razorpay_order['id'],
        )

        # Move cart items → order items
        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
            )
            item.product.stock -= item.quantity
            item.product.save()

        # Clear cart
        items.delete()

        return Response({
            'order': OrderSerializer(order).data,
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_key': settings.RAZORPAY_KEY_ID,
            'amount': int(total * 100),
            'currency': 'INR',
        }, status=201)


class VerifyPaymentView(APIView):
    """
    After Razorpay payment, frontend sends back the 3 fields.
    We verify the signature to confirm payment is genuine.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        razorpay_order_id = request.data.get('razorpay_order_id')
        razorpay_payment_id = request.data.get('razorpay_payment_id')
        razorpay_signature = request.data.get('razorpay_signature')

        # Find order
        try:
            order = Order.objects.get(
                razorpay_order_id=razorpay_order_id,
                user=request.user
            )
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=404)

        # Verify signature
        message = f"{razorpay_order_id}|{razorpay_payment_id}"
        generated_signature = hmac.new(
            settings.RAZORPAY_KEY_SECRET.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

        if generated_signature == razorpay_signature:
            # Payment is genuine ✅
            order.payment_status = 'paid'
            order.status = 'processing'
            order.razorpay_payment_id = razorpay_payment_id
            order.razorpay_signature = razorpay_signature
            order.save()
            return Response({
                'message': 'Payment verified successfully!',
                'order': OrderSerializer(order).data
            })
        else:
            # Payment is fake ❌
            order.payment_status = 'failed'
            order.save()
            return Response({'error': 'Payment verification failed!'}, status=400)


class MyOrdersView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
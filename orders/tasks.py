from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_order_confirmation_email(order_id, user_email, items_summary, total_amount):
    subject = f'Order Confirmation - Order #{order_id}'
    message = f"""
Hi there,

Your order has been placed successfully!

Order ID: #{order_id}
Items: {items_summary}
Total Amount: ₹{total_amount}

Thank you for shopping with us.

Best regards,
E-Commerce Team
    """
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
        fail_silently=False,
    )
    return f"Email sent to {user_email} for order #{order_id}"
from django.db import models
import uuid

from django.conf import settings
from apps.products.models import ProductVariant


class Order(models.Model):

    user = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name="orders"
    )
        

    idempotency_key = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )
    
    checkout_token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )
    
    first_name = models.CharField(
        max_length=100
    )

    last_name = models.CharField(
        max_length=100
    )

    phone = models.CharField(
        max_length=20
    )

    address = models.TextField()

    city = models.CharField(
        max_length=100
    )

    postal_code = models.CharField(
        max_length=20
    )


    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )


    payment_id = models.CharField(
    max_length=255,
    null=True,
    blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    payment_status = models.CharField(
        max_length=20,
        choices=[
            ("unpaid", "پرداخت نشده"),
            ("paid", "پرداخت شده"),
            ("failed", "ناموفق"),
        ],
        default="unpaid"
    )

    def __str__(self):
        return f"Order {self.id}"



class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        related_name="items",
        on_delete=models.CASCADE
    )


    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE
    )


    quantity = models.PositiveIntegerField()


    price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )


    @property
    def subtotal(self):
        return self.price * self.quantity
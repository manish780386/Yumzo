import uuid
from django.db import models


class Order(models.Model):
    """
    One meal delivery instance. For subscribers, these are auto-generated daily
    by a Celery Beat task from their active Subscription. Walk-in (non-subscriber)
    orders also use this model with subscription=None.
    """

    class MealType(models.TextChoices):
        BREAKFAST = "BREAKFAST", "Breakfast"
        LUNCH = "LUNCH", "Lunch"
        DINNER = "DINNER", "Dinner"

    class Status(models.TextChoices):
        SCHEDULED = "SCHEDULED", "Scheduled"
        SKIPPED = "SKIPPED", "Skipped by subscriber"
        PREPARING = "PREPARING", "Being Prepared"
        OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY", "Out for Delivery"
        DELIVERED = "DELIVERED", "Delivered"
        CANCELLED = "CANCELLED", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subscriber = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="orders")
    subscription = models.ForeignKey(
        "subscriptions.Subscription", on_delete=models.SET_NULL, null=True, blank=True, related_name="orders"
    )
    kitchen = models.ForeignKey("kitchens.CloudKitchen", on_delete=models.PROTECT)
    batch = models.ForeignKey(
        "delivery.DeliveryBatch", on_delete=models.SET_NULL, null=True, blank=True, related_name="orders"
    )

    meal_type = models.CharField(max_length=10, choices=MealType.choices)
    scheduled_date = models.DateField(db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)

    delivery_latitude = models.DecimalField(max_digits=9, decimal_places=6)
    delivery_longitude = models.DecimalField(max_digits=9, decimal_places=6)
    delivery_address = models.CharField(max_length=255)

    is_subscriber_order = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)  # 0 for subscriber-covered meals

    delivered_at = models.DateTimeField(null=True, blank=True)
    delivery_otp = models.CharField(max_length=4, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["scheduled_date", "meal_type", "kitchen"]),
        ]

    def __str__(self):
        return f"{self.subscriber} - {self.meal_type} on {self.scheduled_date} ({self.status})"
import uuid
from django.db import models


class CloudKitchen(models.Model):
    """
    A partner cloud kitchen. Each kitchen serves a fixed 3km radius cluster —
    this is the core unit-economics lever (predictable delivery distance).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    owner_name = models.CharField(max_length=150)
    owner_phone = models.CharField(max_length=15)

    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    service_radius_km = models.DecimalField(max_digits=4, decimal_places=2, default=3.0)

    hygiene_score = models.DecimalField(max_digits=3, decimal_places=1, default=5.0)
    is_active = models.BooleanField(default=True)
    accepts_veg = models.BooleanField(default=True)
    accepts_non_veg = models.BooleanField(default=False)
    accepts_jain = models.BooleanField(default=False)

    commission_percent = models.DecimalField(max_digits=4, decimal_places=2, default=18.0)
    max_daily_capacity = models.PositiveIntegerField(default=200)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.service_radius_km}km cluster)"


class MenuItem(models.Model):
    class MealType(models.TextChoices):
        BREAKFAST = "BREAKFAST", "Breakfast"
        LUNCH = "LUNCH", "Lunch"
        DINNER = "DINNER", "Dinner"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    kitchen = models.ForeignKey(CloudKitchen, on_delete=models.CASCADE, related_name="menu_items")
    meal_type = models.CharField(max_length=10, choices=MealType.choices)
    day_of_week = models.PositiveSmallIntegerField(help_text="0=Monday ... 6=Sunday")
    item_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    calories = models.PositiveIntegerField(null=True, blank=True)
    is_available = models.BooleanField(default=True)

    class Meta:
        unique_together = ("kitchen", "meal_type", "day_of_week")

    def __str__(self):
        return f"{self.kitchen.name} - {self.get_meal_type_display()} (Day {self.day_of_week})"


class KitchenReview(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    kitchen = models.ForeignKey(CloudKitchen, on_delete=models.CASCADE, related_name="reviews")
    subscriber = models.ForeignKey("users.User", on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()  # 1-5
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
import uuid
from django.db import models


class RiderCaptain(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField("users.User", on_delete=models.CASCADE, related_name="captain_profile")
    kitchen_cluster = models.ForeignKey(
        "kitchens.CloudKitchen", on_delete=models.SET_NULL, null=True, related_name="captains"
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Captain: {self.user.get_full_name()}"


class Rider(models.Model):
    class VehicleType(models.TextChoices):
        BICYCLE = "BICYCLE", "Bicycle"
        BIKE = "BIKE", "Bike"
        EV = "EV", "Electric Scooter"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField("users.User", on_delete=models.CASCADE, related_name="rider_profile")
    captain = models.ForeignKey(
        RiderCaptain, on_delete=models.SET_NULL, null=True, related_name="riders"
    )
    vehicle_type = models.CharField(max_length=10, choices=VehicleType.choices, default=VehicleType.BIKE)
    is_online = models.BooleanField(default=False)
    current_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    current_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    last_location_update = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Rider: {self.user.get_full_name()}"


class DeliveryBatch(models.Model):
    """
    A group of orders assigned to one rider for one meal-slot run.
    Batching is the core cost-saving mechanism vs. one-order-at-a-time delivery.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rider = models.ForeignKey(Rider, on_delete=models.SET_NULL, null=True, related_name="batches")
    kitchen = models.ForeignKey("kitchens.CloudKitchen", on_delete=models.CASCADE)
    meal_type = models.CharField(max_length=10)
    scheduled_date = models.DateField()
    status = models.CharField(
        max_length=15,
        choices=[
            ("PENDING", "Pending"),
            ("IN_PROGRESS", "In Progress"),
            ("COMPLETED", "Completed"),
        ],
        default="PENDING",
    )
    created_at = models.DateTimeField(auto_now_add=True)
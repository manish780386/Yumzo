import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model. Username field kept for Django admin compatibility,
    but phone number is the actual login identifier for the app.
    """

    class Role(models.TextChoices):
        SUBSCRIBER = "SUBSCRIBER", "Subscriber"
        RIDER = "RIDER", "Rider"
        CAPTAIN = "CAPTAIN", "Rider Captain"
        KITCHEN_OWNER = "KITCHEN_OWNER", "Kitchen Owner"
        ADMIN = "ADMIN", "Admin"

    class DietPreference(models.TextChoices):
        VEG = "VEG", "Vegetarian"
        NON_VEG = "NON_VEG", "Non-Vegetarian"
        JAIN = "JAIN", "Jain"
        EGG = "EGG", "Eggetarian"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=15, unique=True, db_index=True)
    phone_verified = models.BooleanField(default=False)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.SUBSCRIBER)
    diet_preference = models.CharField(
        max_length=10, choices=DietPreference.choices, default=DietPreference.VEG
    )

    # Location — used to auto-match subscriber to nearest 3km cloud-kitchen cluster.
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    address_line = models.CharField(max_length=255, blank=True)
    referral_code = models.CharField(max_length=10, unique=True, null=True, blank=True)
    referred_by = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="referrals"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.role})"


class OTPVerification(models.Model):
    """Short-lived OTP for phone login — verify then issue JWT."""

    phone_number = models.CharField(max_length=15, db_index=True)
    otp_code = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_valid(self):
        from django.utils import timezone

        return not self.is_used and timezone.now() < self.expires_at
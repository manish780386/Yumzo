from django.contrib import admin
from .models import Rider, RiderCaptain, DeliveryBatch


@admin.register(RiderCaptain)
class RiderCaptainAdmin(admin.ModelAdmin):
    list_display = ("user", "kitchen_cluster", "is_active")
    list_filter = ("is_active",)
    search_fields = ("user__phone_number", "user__first_name")


@admin.register(Rider)
class RiderAdmin(admin.ModelAdmin):
    list_display = ("user", "captain", "vehicle_type", "is_online", "last_location_update")
    list_filter = ("vehicle_type", "is_online")
    search_fields = ("user__phone_number", "user__first_name")


@admin.register(DeliveryBatch)
class DeliveryBatchAdmin(admin.ModelAdmin):
    list_display = ("id", "rider", "kitchen", "meal_type", "scheduled_date", "status")
    list_filter = ("status", "meal_type", "scheduled_date")
    date_hierarchy = "scheduled_date"
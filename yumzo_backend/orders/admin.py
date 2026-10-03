from django.contrib import admin
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "subscriber", "kitchen", "meal_type", "scheduled_date",
        "status", "batch", "delivered_at",
    )
    list_filter = ("status", "meal_type", "scheduled_date", "kitchen")
    search_fields = ("subscriber__phone_number", "subscriber__first_name", "delivery_address")
    date_hierarchy = "scheduled_date"
    list_editable = ("status",)  # quick manual status update during pilot phase
    readonly_fields = ("created_at", "delivered_at")
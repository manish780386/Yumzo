from django.contrib import admin
from .models import CloudKitchen, MenuItem, KitchenReview


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 1


@admin.register(CloudKitchen)
class CloudKitchenAdmin(admin.ModelAdmin):
    list_display = ("name", "owner_name", "owner_phone", "service_radius_km", "hygiene_score", "is_active")
    list_filter = ("is_active", "accepts_veg", "accepts_non_veg", "accepts_jain")
    search_fields = ("name", "owner_name", "owner_phone")
    inlines = [MenuItemInline]


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ("item_name", "kitchen", "meal_type", "day_of_week", "is_available")
    list_filter = ("meal_type", "day_of_week", "is_available")
    search_fields = ("item_name", "kitchen__name")


@admin.register(KitchenReview)
class KitchenReviewAdmin(admin.ModelAdmin):
    list_display = ("kitchen", "subscriber", "rating", "created_at")
    list_filter = ("rating",)
    search_fields = ("kitchen__name", "subscriber__phone_number")
from django.contrib import admin
from .models import CloudKitchen, MenuItem, KitchenReview, LastCallDeal


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


@admin.register(LastCallDeal)
class LastCallDealAdmin(admin.ModelAdmin):
    list_display = (
        "kitchen", "deal_date", "meal_type", "item_name", "original_price",
        "discount_percent", "portions_left", "portions_total", "start_time", "is_active",
    )
    list_filter = ("deal_date", "meal_type", "is_active", "kitchen")
    search_fields = ("item_name", "kitchen__name")
    date_hierarchy = "deal_date"
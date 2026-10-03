from rest_framework import serializers
from .models import CloudKitchen, MenuItem, KitchenReview


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ["id", "meal_type", "day_of_week", "item_name", "description", "calories", "is_available"]


class CloudKitchenSerializer(serializers.ModelSerializer):
    distance_km = serializers.FloatField(read_only=True, required=False)
    menu_items = MenuItemSerializer(many=True, read_only=True)

    class Meta:
        model = CloudKitchen
        fields = [
            "id", "name", "latitude", "longitude", "service_radius_km",
            "hygiene_score", "accepts_veg", "accepts_non_veg", "accepts_jain",
            "is_active", "distance_km", "menu_items",
        ]


class KitchenReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = KitchenReview
        fields = ["id", "kitchen", "rating", "comment", "created_at"]
        read_only_fields = ["id", "created_at"]
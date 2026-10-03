from rest_framework import serializers
from .models import Order


class OrderSerializer(serializers.ModelSerializer):
    kitchen_name = serializers.CharField(source="kitchen.name", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "kitchen", "kitchen_name", "meal_type", "scheduled_date",
            "status", "delivery_address", "price", "delivered_at", "created_at",
        ]
        read_only_fields = ["id", "created_at", "delivered_at"]


class MarkDeliveredSerializer(serializers.Serializer):
    order_id = serializers.UUIDField()
    delivery_otp = serializers.CharField(max_length=4)
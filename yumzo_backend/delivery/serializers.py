from rest_framework import serializers
from .models import Rider, RiderCaptain, DeliveryBatch
from orders.serializers import OrderSerializer


class RiderLocationUpdateSerializer(serializers.Serializer):
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6)


class RiderSerializer(serializers.ModelSerializer):
    rider_name = serializers.CharField(source="user.get_full_name", read_only=True)

    class Meta:
        model = Rider
        fields = [
            "id", "rider_name", "vehicle_type", "is_online",
            "current_latitude", "current_longitude", "last_location_update",
        ]


class DeliveryBatchSerializer(serializers.ModelSerializer):
    orders = OrderSerializer(many=True, read_only=True)
    kitchen_name = serializers.CharField(source="kitchen.name", read_only=True)

    class Meta:
        model = DeliveryBatch
        fields = [
            "id", "kitchen", "kitchen_name", "meal_type",
            "scheduled_date", "status", "orders",
        ]


class CaptainTeamSerializer(serializers.ModelSerializer):
    riders = RiderSerializer(many=True, read_only=True)

    class Meta:
        model = RiderCaptain
        fields = ["id", "kitchen_cluster", "is_active", "riders"]
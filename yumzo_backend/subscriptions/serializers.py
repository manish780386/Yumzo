from rest_framework import serializers
from .models import SubscriptionPlan, Subscription, PauseRequest, Wallet


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ["id", "tier", "meals_per_day", "duration_days", "price"]


class CreateSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = [
            "id", "plan", "kitchen", "start_date", "end_date",
            "breakfast_enabled", "lunch_enabled", "dinner_enabled",
            "delivery_latitude", "delivery_longitude", "delivery_address",
            "status", "created_at",
        ]
        read_only_fields = ["id", "end_date", "status", "created_at"]

    def create(self, validated_data):
        from datetime import timedelta
        plan = validated_data["plan"]
        validated_data["end_date"] = validated_data["start_date"] + timedelta(days=plan.duration_days)
        validated_data["subscriber"] = self.context["request"].user
        return super().create(validated_data)


class SubscriptionSerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanSerializer(read_only=True)

    class Meta:
        model = Subscription
        fields = [
            "id", "plan", "kitchen", "status", "start_date", "end_date",
            "breakfast_enabled", "lunch_enabled", "dinner_enabled",
            "delivery_address",
        ]


class PauseRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PauseRequest
        fields = ["id", "subscription", "pause_from", "pause_to", "reason", "created_at"]
        read_only_fields = ["id", "created_at"]


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ["balance", "updated_at"]
from rest_framework import serializers
from .models import User, OTPVerification


class RequestOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)


class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    otp_code = serializers.CharField(max_length=6)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id", "first_name", "last_name", "phone_number", "role",
            "diet_preference", "latitude", "longitude", "address_line",
            "referral_code",
        ]
        read_only_fields = ["id", "phone_number", "role", "referral_code"]
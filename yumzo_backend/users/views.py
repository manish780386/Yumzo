import random
import string
from datetime import timedelta

from django.utils import timezone
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, OTPVerification
from .serializers import RequestOTPSerializer, VerifyOTPSerializer, UserProfileSerializer


class RequestOTPView(APIView):
    """
    Generates a 6-digit OTP and (in production) sends via SMS gateway.
    For dev/testing, OTP is returned in response — remove before production.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RequestOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data["phone_number"]

        otp_code = "".join(random.choices(string.digits, k=6))
        OTPVerification.objects.create(
            phone_number=phone_number,
            otp_code=otp_code,
            expires_at=timezone.now() + timedelta(minutes=5),
        )

        # TODO: integrate SMS gateway (e.g. MSG91, Twilio) here instead of returning OTP
        return Response(
            {"message": "OTP sent", "otp_debug": otp_code},
            status=status.HTTP_200_OK,
        )


class VerifyOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data["phone_number"]
        otp_code = serializer.validated_data["otp_code"]

        otp_entry = (
            OTPVerification.objects.filter(phone_number=phone_number, otp_code=otp_code)
            .order_by("-created_at")
            .first()
        )
        if not otp_entry or not otp_entry.is_valid():
            return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)

        otp_entry.is_used = True
        otp_entry.save(update_fields=["is_used"])

        user, created = User.objects.get_or_create(
            phone_number=phone_number,
            defaults={"username": phone_number, "phone_verified": True},
        )
        if not user.phone_verified:
            user.phone_verified = True
            user.save(update_fields=["phone_verified"])

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "is_new_user": created,
                "user": UserProfileSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Order
from .serializers import OrderSerializer, MarkDeliveredSerializer


class TodayOrdersView(generics.ListAPIView):
    """What's on the subscriber's plate today — shown on the Home screen."""

    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(
            subscriber=self.request.user, scheduled_date=timezone.localdate()
        ).order_by("meal_type")


class OrderHistoryView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(subscriber=self.request.user).order_by("-scheduled_date")


class MarkOrderDeliveredView(APIView):
    """Called by the rider app — OTP confirms the right person received the meal."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = MarkDeliveredSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            order = Order.objects.get(
                id=serializer.validated_data["order_id"],
                status=Order.Status.OUT_FOR_DELIVERY,
            )
        except Order.DoesNotExist:
            return Response({"error": "Order not found or not out for delivery"}, status=400)

        if order.delivery_otp != serializer.validated_data["delivery_otp"]:
            return Response({"error": "Incorrect OTP"}, status=status.HTTP_400_BAD_REQUEST)

        order.status = Order.Status.DELIVERED
        order.delivered_at = timezone.now()
        order.save(update_fields=["status", "delivered_at"])
        return Response({"message": "Delivery confirmed"})
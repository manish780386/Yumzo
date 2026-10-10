import random
import string

from django.db import transaction
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from kitchens.models import LastCallDeal
from kitchens.views import haversine_km
from subscriptions.models import Subscription

from .models import Order
from .serializers import OrderSerializer, MarkDeliveredSerializer


class TodayOrdersView(generics.ListAPIView):
    """What's on the subscriber's plate today."""

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


class ClaimDealView(APIView):
    """
    Buy one portion of a last-call deal (25% off by default, live from 12 PM).
    Creates a one-time Order at the discounted price. Payment is collected on
    delivery for now (UPI/cash) until an online payment gateway is wired in.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        deal_id = request.data.get("deal_id")
        user = request.user
        local_now = timezone.localtime()

        # Where to deliver: active subscription address, else saved profile location.
        subscription = (
            Subscription.objects.filter(subscriber=user, status=Subscription.Status.ACTIVE)
            .order_by("-created_at")
            .first()
        )
        if subscription:
            lat, lng = subscription.delivery_latitude, subscription.delivery_longitude
            address = subscription.delivery_address
        elif user.latitude is not None and user.longitude is not None:
            lat, lng, address = user.latitude, user.longitude, user.address_line or "My location"
        else:
            return Response({"error": "Set your delivery location in your profile first"}, status=400)

        with transaction.atomic():
            try:
                deal = LastCallDeal.objects.select_for_update().select_related("kitchen").get(id=deal_id)
            except (LastCallDeal.DoesNotExist, ValueError):
                return Response({"error": "Deal not found"}, status=404)

            if not deal.is_live(local_now):
                if deal.portions_left < 1:
                    return Response({"error": "Sold out"}, status=400)
                return Response({"error": "This deal is not live right now"}, status=400)

            distance = haversine_km(lat, lng, deal.kitchen.latitude, deal.kitchen.longitude)
            if distance > float(deal.kitchen.service_radius_km):
                return Response({"error": "This kitchen does not deliver to your location"}, status=400)

            already_claimed = Order.objects.filter(
                subscriber=user,
                kitchen=deal.kitchen,
                meal_type=deal.meal_type,
                scheduled_date=deal.deal_date,
                is_subscriber_order=False,
            ).exclude(status=Order.Status.CANCELLED).exists()
            if already_claimed:
                return Response({"error": "You already grabbed this deal today"}, status=400)

            deal.portions_left -= 1
            deal.save(update_fields=["portions_left"])

            order = Order.objects.create(
                subscriber=user,
                subscription=None,
                kitchen=deal.kitchen,
                meal_type=deal.meal_type,
                scheduled_date=deal.deal_date,
                delivery_latitude=lat,
                delivery_longitude=lng,
                delivery_address=address,
                is_subscriber_order=False,
                price=deal.discounted_price,
                delivery_otp="".join(random.choices(string.digits, k=4)),
            )

        return Response(
            {
                "message": "Deal claimed",
                "order_id": str(order.id),
                "price": str(order.price),
                "portions_left": deal.portions_left,
            },
            status=status.HTTP_201_CREATED,
        )
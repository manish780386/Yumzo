from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import SubscriptionPlan, Subscription, PauseRequest, Wallet
from .serializers import (
    SubscriptionPlanSerializer,
    CreateSubscriptionSerializer,
    SubscriptionSerializer,
    PauseRequestSerializer,
    WalletSerializer,
)
from orders.models import Order
from orders.rules import can_skip


class SubscriptionPlanListView(generics.ListAPIView):
    queryset = SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.IsAuthenticated]


class CreateSubscriptionView(generics.CreateAPIView):
    serializer_class = CreateSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]


class MySubscriptionView(generics.RetrieveAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return (
            Subscription.objects.filter(subscriber=self.request.user, status="ACTIVE")
            .order_by("-created_at")
            .first()
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            return Response({"detail": "No active subscription"}, status=status.HTTP_404_NOT_FOUND)
        return Response(self.get_serializer(instance).data)


class CreatePauseRequestView(generics.CreateAPIView):
    """
    Pausing a subscription cancels (sets status SKIPPED) any already-scheduled
    orders in that date range — this is the #1 retention feature for subscribers
    who travel home or have exams.
    """

    serializer_class = PauseRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        pause_request = serializer.save()
        Order.objects.filter(
            subscription=pause_request.subscription,
            scheduled_date__range=[pause_request.pause_from, pause_request.pause_to],
            status=Order.Status.SCHEDULED,
        ).update(status=Order.Status.SKIPPED)


class SkipTodayMealView(APIView):
    """Quick single-day skip, e.g. 'skip today's lunch'."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        order_id = request.data.get("order_id")
        try:
            order = Order.objects.get(id=order_id, subscriber=request.user, status=Order.Status.SCHEDULED)
        except Order.DoesNotExist:
            return Response({"error": "Order not found or cannot be skipped"}, status=400)

        if not can_skip(order.meal_type, order.scheduled_date):
            return Response(
                {"error": "Too late to skip this meal - the kitchen has already planned it"},
                status=400,
            )

        order.status = Order.Status.SKIPPED
        order.save(update_fields=["status"])
        return Response({"message": "Meal skipped"})


class MyWalletView(generics.RetrieveAPIView):
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        wallet, _ = Wallet.objects.get_or_create(user=self.request.user)
        return wallet
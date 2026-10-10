from datetime import timedelta
from math import radians, sin, cos, sqrt, atan2

from django.utils import timezone
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import Order
from orders.rules import MEAL_ORDER, can_skip, skip_cutoff
from subscriptions.models import Subscription

from .models import CloudKitchen, LastCallDeal, MenuItem
from .serializers import CloudKitchenSerializer


def haversine_km(lat1, lon1, lat2, lon2):
    """Great-circle distance between two lat/lng points, in km."""
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


class NearbyKitchensView(APIView):
    """
    Returns active kitchens whose service_radius_km covers the given point,
    sorted by distance. This is the core "which cluster do I belong to" lookup.

    NOTE: For production scale, replace this loop with a PostGIS
    ST_DWithin query on a PointField for proper spatial indexing.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            lat = float(request.query_params["lat"])
            lng = float(request.query_params["lng"])
        except (KeyError, ValueError):
            return Response({"error": "lat and lng query params are required"}, status=400)

        results = []
        for kitchen in CloudKitchen.objects.filter(is_active=True):
            distance = haversine_km(lat, lng, kitchen.latitude, kitchen.longitude)
            if distance <= float(kitchen.service_radius_km):
                kitchen.distance_km = round(distance, 2)
                results.append(kitchen)

        results.sort(key=lambda k: k.distance_km)
        serializer = CloudKitchenSerializer(results, many=True)
        return Response(serializer.data)


class KitchenDetailView(generics.RetrieveAPIView):
    queryset = CloudKitchen.objects.filter(is_active=True)
    serializer_class = CloudKitchenSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"


def _kitchen_for_user(user, subscription):
    """Subscribed kitchen if any, else the nearest kitchen covering the user's saved location."""
    if subscription and subscription.kitchen:
        return subscription.kitchen
    if user.latitude is None or user.longitude is None:
        return None
    covering = []
    for kitchen in CloudKitchen.objects.filter(is_active=True):
        distance = haversine_km(user.latitude, user.longitude, kitchen.latitude, kitchen.longitude)
        if distance <= float(kitchen.service_radius_km):
            covering.append((distance, kitchen))
    covering.sort(key=lambda pair: pair[0])
    return covering[0][1] if covering else None


class TodayMenuView(APIView):
    """
    One call that powers the Home screen: today's menu per meal (with the
    subscriber's order status and skip cutoff), last-call deals (live after
    the deal start time, 12:00 by default), and a peek at tomorrow's menu.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        local_now = timezone.localtime()
        today = local_now.date()
        tomorrow = today + timedelta(days=1)

        subscription = (
            Subscription.objects.filter(
                subscriber=request.user,
                status=Subscription.Status.ACTIVE,
                start_date__lte=today,
                end_date__gte=today,
            )
            .select_related("kitchen")
            .order_by("-created_at")
            .first()
        )
        kitchen = _kitchen_for_user(request.user, subscription)

        payload = {
            "date": today.isoformat(),
            "weekday": local_now.strftime("%A"),
            "server_time": local_now.strftime("%H:%M"),
            "has_subscription": subscription is not None,
            "kitchen": None,
            "meals": [],
            "deals": [],
            "tomorrow": [],
        }
        if not kitchen:
            return Response(payload)

        payload["kitchen"] = {"id": str(kitchen.id), "name": kitchen.name}

        # --- Today's menu, joined with this user's own orders ---
        todays_orders = {}
        for order in Order.objects.filter(
            subscriber=request.user, scheduled_date=today, is_subscriber_order=True
        ).order_by("created_at"):
            todays_orders[order.meal_type] = order

        menu_today = {
            item.meal_type: item
            for item in MenuItem.objects.filter(
                kitchen=kitchen, day_of_week=today.weekday(), is_available=True
            )
        }
        for meal_type in MEAL_ORDER:
            item = menu_today.get(meal_type)
            if not item:
                continue
            order = todays_orders.get(meal_type)
            skippable = bool(
                order
                and order.status == Order.Status.SCHEDULED
                and can_skip(meal_type, today, local_now)
            )
            payload["meals"].append({
                "meal_type": meal_type,
                "item_name": item.item_name,
                "description": item.description,
                "calories": item.calories,
                "order": {"id": str(order.id), "status": order.status} if order else None,
                "can_skip": skippable,
                "skip_cutoff": skip_cutoff(meal_type, today).astimezone(local_now.tzinfo).strftime("%I:%M %p"),
            })

        # --- Last-call deals ---
        deals = LastCallDeal.objects.filter(
            kitchen=kitchen, deal_date=today, is_active=True, portions_left__gt=0
        ).order_by("start_time")
        for deal in deals:
            payload["deals"].append({
                "id": str(deal.id),
                "meal_type": deal.meal_type,
                "item_name": deal.item_name,
                "original_price": str(deal.original_price),
                "discounted_price": str(deal.discounted_price),
                "discount_percent": deal.discount_percent,
                "portions_left": deal.portions_left,
                "unlocks_at": deal.start_time.strftime("%I:%M %p").lstrip("0"),
                "is_live": deal.is_live(local_now),
            })

        # --- Tomorrow's menu preview ---
        menu_tomorrow = MenuItem.objects.filter(
            kitchen=kitchen, day_of_week=tomorrow.weekday(), is_available=True
        )
        by_type = {item.meal_type: item for item in menu_tomorrow}
        for meal_type in MEAL_ORDER:
            if meal_type in by_type:
                payload["tomorrow"].append({
                    "meal_type": meal_type,
                    "item_name": by_type[meal_type].item_name,
                })

        return Response(payload)
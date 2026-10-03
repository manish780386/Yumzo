from django.utils import timezone
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import Rider, RiderCaptain, DeliveryBatch
from .serializers import RiderLocationUpdateSerializer, DeliveryBatchSerializer, CaptainTeamSerializer
from orders.models import Order


class UpdateRiderLocationView(APIView):
    """
    Called frequently (every ~10-15s) by the rider app while on a delivery run.
    Updates the DB (so late-joining trackers get the last known point) and
    broadcasts the new position over the batch's Channels group for anyone
    already connected via WebSocket (subscriber's live-tracking screen).
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = RiderLocationUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        rider = Rider.objects.get(user=request.user)
        rider.current_latitude = serializer.validated_data["latitude"]
        rider.current_longitude = serializer.validated_data["longitude"]
        rider.last_location_update = timezone.now()
        rider.save(update_fields=["current_latitude", "current_longitude", "last_location_update"])

        # Broadcast to any active batch this rider is currently running, so
        # subscribers watching that batch's tracking screen get a live update.
        active_batch = DeliveryBatch.objects.filter(
            rider=rider, status="IN_PROGRESS", scheduled_date=timezone.localdate()
        ).first()

        if active_batch:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"batch_{active_batch.id}",
                {
                    "type": "rider_location",
                    "lat": str(rider.current_latitude),
                    "lng": str(rider.current_longitude),
                    "rider_id": str(rider.id),
                },
            )

        return Response({"message": "Location updated"})


class MyBatchesTodayView(generics.ListAPIView):
    """A rider's assigned delivery batches (routes) for today, with order stop-list."""

    serializer_class = DeliveryBatchSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        rider = Rider.objects.get(user=self.request.user)
        return DeliveryBatch.objects.filter(
            rider=rider, scheduled_date=timezone.localdate()
        ).prefetch_related("orders")


class MyCaptainTeamView(generics.RetrieveAPIView):
    """Captain's view of their assigned riders and current status — for the captain dashboard."""

    serializer_class = CaptainTeamSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return RiderCaptain.objects.prefetch_related("riders").get(user=self.request.user)
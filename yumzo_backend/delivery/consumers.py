import json
from channels.generic.websocket import AsyncWebsocketConsumer


class RiderTrackingConsumer(AsyncWebsocketConsumer):
    """
    WebSocket group per delivery batch: group name "batch_<batch_id>".

    - Rider app connects and calls `send_location` repeatedly while on a run.
    - Subscriber app connects read-only to the same group to watch the rider
      move live on their order-tracking screen.

    Flow:
      1. Rider/Subscriber connect to ws://.../ws/track/<batch_id>/
      2. Rider sends: {"type": "location_update", "lat": .., "lng": ..}
      3. Everyone in that group (incl. subscriber) receives the broadcast
    """

    async def connect(self):
        self.batch_id = self.scope["url_route"]["kwargs"]["batch_id"]
        self.group_name = f"batch_{self.batch_id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)

        if data.get("type") == "location_update":
            # Broadcast rider's new position to everyone tracking this batch
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "rider_location",
                    "lat": data.get("lat"),
                    "lng": data.get("lng"),
                    "rider_id": data.get("rider_id"),
                },
            )

    # Handler name must match the "type" key used in group_send (dots -> underscores)
    async def rider_location(self, event):
        await self.send(text_data=json.dumps({
            "type": "rider_location",
            "lat": event["lat"],
            "lng": event["lng"],
            "rider_id": event.get("rider_id"),
        }))
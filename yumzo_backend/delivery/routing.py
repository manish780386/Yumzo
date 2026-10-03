from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/track/(?P<batch_id>[0-9a-f-]+)/$", consumers.RiderTrackingConsumer.as_asgi()),
]
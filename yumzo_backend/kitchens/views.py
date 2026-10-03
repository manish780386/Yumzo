from math import radians, sin, cos, sqrt, atan2

from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CloudKitchen
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
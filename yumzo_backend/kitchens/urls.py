from django.urls import path
from .views import NearbyKitchensView, KitchenDetailView

urlpatterns = [
    path("nearby/", NearbyKitchensView.as_view(), name="nearby-kitchens"),
    path("<uuid:id>/", KitchenDetailView.as_view(), name="kitchen-detail"),
]
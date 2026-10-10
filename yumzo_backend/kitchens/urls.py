from django.urls import path
from .views import NearbyKitchensView, KitchenDetailView, TodayMenuView

urlpatterns = [
    path("nearby/", NearbyKitchensView.as_view(), name="nearby-kitchens"),
    path("today/", TodayMenuView.as_view(), name="today-menu"),
    path("<uuid:id>/", KitchenDetailView.as_view(), name="kitchen-detail"),
]
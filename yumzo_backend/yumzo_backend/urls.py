from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/users/", include("users.urls")),
    path("api/kitchens/", include("kitchens.urls")),
    path("api/subscriptions/", include("subscriptions.urls")),
    path("api/orders/", include("orders.urls")),
    path("api/delivery/", include("delivery.urls")),
]
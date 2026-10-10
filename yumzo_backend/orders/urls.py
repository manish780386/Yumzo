from django.urls import path
from .views import TodayOrdersView, OrderHistoryView, MarkOrderDeliveredView, ClaimDealView

urlpatterns = [
    path("today/", TodayOrdersView.as_view(), name="today-orders"),
    path("history/", OrderHistoryView.as_view(), name="order-history"),
    path("mark-delivered/", MarkOrderDeliveredView.as_view(), name="mark-delivered"),
    path("claim-deal/", ClaimDealView.as_view(), name="claim-deal"),
]
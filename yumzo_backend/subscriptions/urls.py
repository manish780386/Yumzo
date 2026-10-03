from django.urls import path
from .views import (
    SubscriptionPlanListView,
    CreateSubscriptionView,
    MySubscriptionView,
    CreatePauseRequestView,
    SkipTodayMealView,
    MyWalletView,
)

urlpatterns = [
    path("plans/", SubscriptionPlanListView.as_view(), name="plan-list"),
    path("subscribe/", CreateSubscriptionView.as_view(), name="subscribe"),
    path("my-subscription/", MySubscriptionView.as_view(), name="my-subscription"),
    path("pause/", CreatePauseRequestView.as_view(), name="pause-subscription"),
    path("skip-meal/", SkipTodayMealView.as_view(), name="skip-meal"),
    path("wallet/", MyWalletView.as_view(), name="wallet"),
]
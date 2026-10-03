from django.urls import path
from .views import UpdateRiderLocationView, MyBatchesTodayView, MyCaptainTeamView

urlpatterns = [
    path("update-location/", UpdateRiderLocationView.as_view(), name="update-location"),
    path("my-batches/", MyBatchesTodayView.as_view(), name="my-batches"),
    path("my-team/", MyCaptainTeamView.as_view(), name="my-team"),
]
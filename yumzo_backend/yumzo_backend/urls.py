from django.contrib import admin
from django.urls import path
from .welcome import welcome

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", welcome),
]

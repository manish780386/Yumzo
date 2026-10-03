from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, OTPVerification


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("phone_number", "first_name", "last_name", "role", "diet_preference", "phone_verified", "is_active")
    list_filter = ("role", "diet_preference", "phone_verified")
    search_fields = ("phone_number", "first_name", "last_name", "username")
    ordering = ("-created_at",)

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "phone_number", "email")}),
        ("Role & preferences", {"fields": ("role", "diet_preference", "latitude", "longitude", "address_line")}),
        ("Referral", {"fields": ("referral_code", "referred_by")}),
        ("Status", {"fields": ("phone_verified", "is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "phone_number", "password1", "password2", "role"),
        }),
    )


@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ("phone_number", "otp_code", "is_used", "created_at", "expires_at")
    list_filter = ("is_used",)
    search_fields = ("phone_number",)
    readonly_fields = ("created_at",)
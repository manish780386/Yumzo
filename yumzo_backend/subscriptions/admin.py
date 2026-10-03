from django.contrib import admin
from .models import SubscriptionPlan, Subscription, PauseRequest, Wallet, WalletTransaction


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ("tier", "meals_per_day", "duration_days", "price", "is_active")
    list_filter = ("tier", "is_active")


class PauseRequestInline(admin.TabularInline):
    model = PauseRequest
    extra = 0


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("subscriber", "plan", "kitchen", "status", "start_date", "end_date")
    list_filter = ("status", "plan__tier")
    search_fields = ("subscriber__phone_number", "subscriber__first_name")
    inlines = [PauseRequestInline]


@admin.register(PauseRequest)
class PauseRequestAdmin(admin.ModelAdmin):
    list_display = ("subscription", "pause_from", "pause_to", "created_at")
    search_fields = ("subscription__subscriber__phone_number",)


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("user", "balance", "updated_at")
    search_fields = ("user__phone_number",)


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ("wallet", "txn_type", "amount", "created_at")
    list_filter = ("txn_type",)
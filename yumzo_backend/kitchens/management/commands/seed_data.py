"""
Seeds minimal test data so you can exercise the full app flow:
one cloud kitchen (centered on SVVV, Indore) and three subscription plans.

Run with:
    python manage.py seed_data
"""

from django.core.management.base import BaseCommand
from kitchens.models import CloudKitchen, MenuItem
from subscriptions.models import SubscriptionPlan


class Command(BaseCommand):
    help = "Seed test data: one cloud kitchen + subscription plans"

    def handle(self, *args, **options):
        # SVVV Indore coordinates — adjust if you want the test kitchen
        # centered somewhere else for your pilot area.
        kitchen, created = CloudKitchen.objects.get_or_create(
            name="Test Kitchen - SVVV Area",
            defaults={
                "owner_name": "Test Owner",
                "owner_phone": "9000000000",
                "latitude": 22.6499,
                "longitude": 75.8898,
                "service_radius_km": 3.0,
                "hygiene_score": 4.5,
                "is_active": True,
                "accepts_veg": True,
                "accepts_non_veg": True,
                "accepts_jain": True,
                "commission_percent": 18.0,
                "max_daily_capacity": 200,
            },
        )
        self.stdout.write(
            self.style.SUCCESS(f"{'Created' if created else 'Found existing'} kitchen: {kitchen.name}")
        )

        # A simple one-day menu so MenuItem rows exist for day_of_week=0 (Monday)
        menu_items = [
            (MenuItem.MealType.BREAKFAST, "Poha + Jalebi"),
            (MenuItem.MealType.LUNCH, "Dal, Rice, Roti, Sabzi"),
            (MenuItem.MealType.DINNER, "Paneer Curry, Roti, Rice"),
        ]
        for meal_type, item_name in menu_items:
            MenuItem.objects.get_or_create(
                kitchen=kitchen,
                meal_type=meal_type,
                day_of_week=0,
                defaults={"item_name": item_name, "is_available": True},
            )

        plans_data = [
            (SubscriptionPlan.PlanTier.BASIC, 1, 30, 1800),
            (SubscriptionPlan.PlanTier.STANDARD, 2, 30, 3200),
            (SubscriptionPlan.PlanTier.PREMIUM, 3, 30, 4500),
        ]
        for tier, meals, duration, price in plans_data:
            plan, created = SubscriptionPlan.objects.get_or_create(
                tier=tier,
                defaults={
                    "meals_per_day": meals,
                    "duration_days": duration,
                    "price": price,
                    "is_active": True,
                },
            )
            self.stdout.write(
                self.style.SUCCESS(f"{'Created' if created else 'Found existing'} plan: {plan.tier} - ₹{plan.price}")
            )

        self.stdout.write(self.style.SUCCESS("\nSeed complete. Open the Plans screen in the app to see these."))
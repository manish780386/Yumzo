"""
Seeds test data so you can exercise the full app flow:
one cloud kitchen (near SVVV, Indore), a full week of menus, three
subscription plans, and today's last-call deals.

Safe to re-run: it never duplicates anything. Re-run it each day while testing
to get a fresh set of deals for that day.

    python manage.py seed_data
"""

from django.core.management.base import BaseCommand
from django.utils import timezone

from kitchens.models import CloudKitchen, LastCallDeal, MenuItem
from subscriptions.models import SubscriptionPlan

# day_of_week: 0=Monday ... 6=Sunday -> (breakfast, lunch, dinner)
WEEK_MENU = {
    0: ("Poha + Jalebi", "Dal Tadka, Jeera Rice, Roti, Aloo Gobhi", "Paneer Butter Masala, Roti, Rice"),
    1: ("Upma + Chutney", "Rajma, Rice, Roti, Salad", "Mix Veg, Dal Fry, Roti, Rice"),
    2: ("Aloo Paratha + Curd", "Kadhi Pakoda, Rice, Roti", "Chole, Bhature, Raita"),
    3: ("Sabudana Khichdi", "Dal Makhani, Rice, Roti, Bhindi", "Palak Paneer, Roti, Jeera Rice"),
    4: ("Poha + Sev", "Chana Masala, Rice, Roti, Salad", "Veg Pulao, Raita, Papad"),
    5: ("Misal Pav", "Paneer Bhurji, Roti, Dal, Rice", "Dal Baati Churma"),
    6: ("Idli Sambar", "Veg Biryani, Raita, Salad", "Pav Bhaji, Pulao"),
}
MEAL_TYPES = [MenuItem.MealType.BREAKFAST, MenuItem.MealType.LUNCH, MenuItem.MealType.DINNER]


class Command(BaseCommand):
    help = "Seed test data: kitchen, weekly menu, plans, and today's last-call deals"

    def handle(self, *args, **options):
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

        for day, names in WEEK_MENU.items():
            for meal_type, item_name in zip(MEAL_TYPES, names):
                MenuItem.objects.get_or_create(
                    kitchen=kitchen,
                    meal_type=meal_type,
                    day_of_week=day,
                    defaults={"item_name": item_name, "is_available": True},
                )
        self.stdout.write(self.style.SUCCESS("Weekly menu ready (7 days x 3 meals)"))

        plans_data = [
            (SubscriptionPlan.PlanTier.BASIC, 1, 30, 1800),
            (SubscriptionPlan.PlanTier.STANDARD, 2, 30, 3200),
            (SubscriptionPlan.PlanTier.PREMIUM, 3, 30, 4500),
        ]
        for tier, meals, duration, price in plans_data:
            plan, plan_created = SubscriptionPlan.objects.get_or_create(
                tier=tier,
                defaults={
                    "meals_per_day": meals,
                    "duration_days": duration,
                    "price": price,
                    "is_active": True,
                },
            )
            self.stdout.write(
                self.style.SUCCESS(f"{'Created' if plan_created else 'Found existing'} plan: {plan.tier} - Rs {plan.price}")
            )

        # Today's surplus deals: lunch + dinner, 25% off from 12:00 noon.
        today = timezone.localdate()
        todays_menu = {
            item.meal_type: item
            for item in MenuItem.objects.filter(kitchen=kitchen, day_of_week=today.weekday())
        }
        for meal_type, price, portions in [
            (MenuItem.MealType.LUNCH, 120, 15),
            (MenuItem.MealType.DINNER, 140, 10),
        ]:
            item = todays_menu.get(meal_type)
            if not item:
                continue
            deal, deal_created = LastCallDeal.objects.get_or_create(
                kitchen=kitchen,
                deal_date=today,
                meal_type=meal_type,
                defaults={
                    "item_name": item.item_name,
                    "original_price": price,
                    "discount_percent": 25,
                    "portions_total": portions,
                    "portions_left": portions,
                },
            )
            self.stdout.write(
                self.style.SUCCESS(f"{'Created' if deal_created else 'Found existing'} deal: {deal}")
            )

        self.stdout.write(self.style.SUCCESS("\nSeed complete. Pull to refresh the Home screen in the app."))
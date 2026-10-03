import random
import string

from celery import shared_task
from django.utils import timezone

from subscriptions.models import Subscription
from .models import Order


@shared_task
def generate_tomorrows_orders():
    """
    Runs every night (via Celery Beat, e.g. at 9 PM) for every ACTIVE
    subscription: creates tomorrow's Order rows for each enabled meal type,
    unless the subscriber already has a pause covering that date.

    Scheduling example (settings.py CELERY_BEAT_SCHEDULE):
        'generate-daily-orders': {
            'task': 'orders.tasks.generate_tomorrows_orders',
            'schedule': crontab(hour=21, minute=0),
        }
    """
    tomorrow = timezone.localdate() + timezone.timedelta(days=1)
    created_count = 0

    active_subscriptions = Subscription.objects.filter(
        status=Subscription.Status.ACTIVE,
        start_date__lte=tomorrow,
        end_date__gte=tomorrow,
    ).select_related("kitchen", "subscriber")

    for sub in active_subscriptions:
        is_paused = sub.pause_requests.filter(
            pause_from__lte=tomorrow, pause_to__gte=tomorrow
        ).exists()
        if is_paused or not sub.kitchen:
            continue

        meal_flags = [
            (sub.breakfast_enabled, Order.MealType.BREAKFAST),
            (sub.lunch_enabled, Order.MealType.LUNCH),
            (sub.dinner_enabled, Order.MealType.DINNER),
        ]
        for enabled, meal_type in meal_flags:
            if not enabled:
                continue
            already_exists = Order.objects.filter(
                subscription=sub, scheduled_date=tomorrow, meal_type=meal_type
            ).exists()
            if already_exists:
                continue

            Order.objects.create(
                subscriber=sub.subscriber,
                subscription=sub,
                kitchen=sub.kitchen,
                meal_type=meal_type,
                scheduled_date=tomorrow,
                delivery_latitude=sub.delivery_latitude,
                delivery_longitude=sub.delivery_longitude,
                delivery_address=sub.delivery_address,
                is_subscriber_order=True,
                price=0,
                delivery_otp="".join(random.choices(string.digits, k=4)),
            )
            created_count += 1

    return f"Generated {created_count} orders for {tomorrow}"


@shared_task
def expire_old_subscriptions():
    """Runs daily — flips subscriptions past their end_date to EXPIRED."""
    today = timezone.localdate()
    updated = Subscription.objects.filter(
        status=Subscription.Status.ACTIVE, end_date__lt=today
    ).update(status=Subscription.Status.EXPIRED)
    return f"Expired {updated} subscriptions"
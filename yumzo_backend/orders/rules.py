"""
Business rules in one place so the API and the app agree. Tune these as the
pilot teaches you what the kitchens actually need.
"""

from datetime import datetime, time, timedelta

from django.utils import timezone

# A subscriber can skip a meal only until its cutoff, so the kitchen knows
# the headcount before it starts cooking.
#   (days_before_meal_date, time_of_day)
SKIP_CUTOFFS = {
    "BREAKFAST": (1, time(21, 0)),  # previous night 9 PM
    "LUNCH": (0, time(9, 0)),       # same day 9 AM
    "DINNER": (0, time(15, 0)),     # same day 3 PM
}

MEAL_ORDER = ["BREAKFAST", "LUNCH", "DINNER"]


def skip_cutoff(meal_type, meal_date):
    """Timezone-aware datetime after which this meal can no longer be skipped."""
    days_before, cutoff_time = SKIP_CUTOFFS[meal_type]
    naive = datetime.combine(meal_date - timedelta(days=days_before), cutoff_time)
    return timezone.make_aware(naive)


def can_skip(meal_type, meal_date, now=None):
    now = now or timezone.now()
    return now < skip_cutoff(meal_type, meal_date)
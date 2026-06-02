from datetime import datetime, timedelta
from django.utils import timezone
from .models import Availability, TimeOff
from appointments.models import Appointment


BLOCKING_STATUSES = [Appointment.Status.PENDING, Appointment.Status.CONFIRMED]


def generate_slots_for_doctor(doctor, target_date):
    """Retourne les créneaux libres pour un médecin et une date donnés."""
    today = timezone.localdate()
    if target_date < today:
        return []

    if TimeOff.objects.filter(doctor=doctor, start_date__lte=target_date, end_date__gte=target_date).exists():
        return []

    availabilities = Availability.objects.filter(doctor=doctor, weekday=target_date.weekday(), is_active=True)
    if not availabilities.exists():
        return []

    booked = set(
        Appointment.objects.filter(doctor=doctor, date=target_date, status__in=BLOCKING_STATUSES)
        .values_list('time', flat=True)
    )

    slots = []
    current_dt = timezone.localtime()
    for availability in availabilities:
        current = datetime.combine(target_date, availability.start_time)
        end = datetime.combine(target_date, availability.end_time)
        delta = timedelta(minutes=availability.slot_duration_minutes)
        while current + delta <= end:
            slot_time = current.time()
            is_future = target_date > today or current.time() > current_dt.time()
            if is_future and slot_time not in booked:
                slots.append(slot_time)
            current += delta

    return sorted(set(slots))

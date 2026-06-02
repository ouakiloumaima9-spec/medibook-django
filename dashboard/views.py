from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import redirect, render
from django.utils import timezone
from accounts.models import User
from appointments.models import Appointment
from doctors.models import Doctor, Specialty


def home(request):
    if not request.user.is_authenticated:
        return render(request, 'dashboard/landing.html', {
            'doctors_count': Doctor.objects.filter(is_active=True).count(),
            'specialties_count': Specialty.objects.filter(is_active=True).count(),
            'featured_specialties': Specialty.objects.filter(is_active=True)[:6],
        })
    if request.user.is_patient():
        return patient_dashboard(request)
    if request.user.is_doctor():
        return doctor_dashboard(request)
    if request.user.is_admin_user():
        return admin_dashboard(request)
    return redirect('accounts:login')


@login_required
def patient_dashboard(request):
    user = request.user
    today = timezone.localdate()
    appointments = Appointment.objects.filter(patient=user).select_related('doctor__user', 'specialty')
    upcoming = appointments.filter(date__gte=today, status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED]).order_by('date', 'time')
    past = appointments.filter(Q(date__lt=today) | Q(status__in=[Appointment.Status.COMPLETED, Appointment.Status.NO_SHOW]))
    cancelled = appointments.filter(status=Appointment.Status.CANCELLED)
    return render(request, 'dashboard/patient.html', {
        'upcoming': upcoming,
        'upcoming_count': upcoming.count(),
        'confirmed_count': upcoming.filter(status=Appointment.Status.CONFIRMED).count(),
        'past_count': past.count(),
        'cancelled_count': cancelled.count(),
        'next_appointment': upcoming.first(),
        'recent_appointments': appointments.order_by('-date', '-time')[:5],
        'unread_notifications': request.user.notifications.filter(is_read=False)[:5],
    })


@login_required
def doctor_dashboard(request):
    doctor = request.user.doctor_profile
    today = timezone.localdate()
    week_end = today + timedelta(days=7)
    appointments = Appointment.objects.filter(doctor=doctor).select_related('patient', 'specialty')
    today_appointments = appointments.filter(date=today).order_by('time')
    week_appointments = appointments.filter(date__gte=today, date__lte=week_end).order_by('date', 'time')
    unique_patients_count = appointments.values('patient').distinct().count()
    return render(request, 'dashboard/doctor.html', {
        'doctor': doctor,
        'today_appointments': today_appointments,
        'week_appointments': week_appointments,
        'today_count': today_appointments.count(),
        'week_count': week_appointments.count(),
        'total_count': appointments.count(),
        'confirmed_count': appointments.filter(status=Appointment.Status.CONFIRMED).count(),
        'cancelled_count': appointments.filter(status=Appointment.Status.CANCELLED).count(),
        'unique_patients_count': unique_patients_count,
        'availabilities': doctor.availabilities.all(),
    })


@login_required
def admin_dashboard(request):
    if not request.user.is_admin_user():
        return redirect('dashboard:home')
    return render(request, 'dashboard/admin.html', {
        'total_patients': User.objects.filter(role=User.Role.PATIENT).count(),
        'total_doctors': Doctor.objects.count(),
        'active_doctors': Doctor.objects.filter(is_active=True).count(),
        'total_appointments': Appointment.objects.count(),
        'by_status': Appointment.objects.values('status').annotate(c=Count('id')).order_by('status'),
        'by_specialty': Appointment.objects.values('specialty__name').annotate(c=Count('id')).order_by('-c')[:10],
        'top_doctors': Doctor.objects.select_related('user').annotate(c=Count('appointments')).order_by('-c')[:10],
        'latest_appointments': Appointment.objects.select_related('patient', 'doctor__user', 'specialty').order_by('-created_at')[:8],
    })

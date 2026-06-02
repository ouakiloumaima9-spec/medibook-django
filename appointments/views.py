from datetime import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from doctors.models import Doctor
from schedules.utils import generate_slots_for_doctor
from .forms import AppointmentBookingForm, AppointmentFilterForm, ConsultationForm, ReviewForm
from .models import Appointment, Consultation


def _parse_date(value):
    if not value:
        return timezone.localdate()
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError:
        return timezone.localdate()


def _parse_time(value):
    if not value:
        return None
    for fmt in ('%H:%M', '%H:%M:%S'):
        try:
            return datetime.strptime(value, fmt).time()
        except ValueError:
            continue
    return None


def _appointment_for_user_or_403(request, pk):
    appointment = get_object_or_404(
        Appointment.objects.select_related('patient', 'doctor__user', 'specialty'),
        pk=pk,
    )
    user = request.user
    if user.is_admin_user():
        return appointment
    if user.is_patient() and appointment.patient_id == user.id:
        return appointment
    if user.is_doctor() and hasattr(user, 'doctor_profile') and appointment.doctor_id == user.doctor_profile.id:
        return appointment
    raise PermissionDenied('Vous n’avez pas accès à ce rendez-vous.')


@login_required
def book_appointment(request, doctor_id):
    if not request.user.is_patient():
        messages.error(request, 'Seuls les patients peuvent réserver un rendez-vous.')
        return redirect('dashboard:home')

    doctor = get_object_or_404(Doctor.objects.prefetch_related('specialties'), pk=doctor_id, is_active=True)
    selected_date = _parse_date(request.GET.get('date'))
    selected_time = _parse_time(request.POST.get('selected_time') or request.GET.get('time'))
    slots = generate_slots_for_doctor(doctor, selected_date)

    if request.method == 'POST':
        form = AppointmentBookingForm(request.POST)
        if not selected_time:
            messages.error(request, 'Veuillez choisir un créneau disponible.')
        elif selected_time not in slots:
            messages.error(request, 'Ce créneau n’est plus disponible. Veuillez en choisir un autre.')
        elif form.is_valid():
            try:
                with transaction.atomic():
                    appointment = form.save(commit=False)
                    appointment.patient = request.user
                    appointment.doctor = doctor
                    appointment.date = selected_date
                    appointment.time = selected_time
                    appointment.specialty = doctor.specialties.first()
                    appointment.full_clean()
                    appointment.save()
                messages.success(request, 'Rendez-vous réservé avec succès. Une notification de confirmation a été créée.')
                return redirect('appointments:detail', pk=appointment.pk)
            except ValidationError as exc:
                messages.error(request, ' '.join(exc.messages) if hasattr(exc, 'messages') else str(exc))
    else:
        form = AppointmentBookingForm()

    return render(request, 'appointments/book.html', {
        'doctor': doctor,
        'slots': slots,
        'selected_date': selected_date,
        'selected_time': selected_time.strftime('%H:%M') if selected_time else '',
        'form': form,
    })


@login_required
def appointment_detail(request, pk):
    appointment = _appointment_for_user_or_403(request, pk)
    return render(request, 'appointments/detail.html', {
        'appointment': appointment,
        'can_cancel': appointment.can_be_cancelled and (request.user.is_admin_user() or appointment.patient_id == request.user.id or appointment.doctor.user_id == request.user.id),
        'can_reschedule': appointment.can_be_rescheduled and request.user.is_patient() and appointment.patient_id == request.user.id,
        'can_confirm': request.user.is_doctor() and appointment.doctor.user_id == request.user.id and appointment.status == Appointment.Status.PENDING,
        'can_complete': request.user.is_doctor() and appointment.doctor.user_id == request.user.id and appointment.status == Appointment.Status.CONFIRMED,
        'can_no_show': request.user.is_doctor() and appointment.doctor.user_id == request.user.id and appointment.status in [Appointment.Status.PENDING, Appointment.Status.CONFIRMED],
        'can_review': request.user.is_patient() and appointment.patient_id == request.user.id and appointment.status == Appointment.Status.COMPLETED and not hasattr(appointment, 'review'),
        'can_add_consultation': request.user.is_doctor() and appointment.doctor.user_id == request.user.id and appointment.status in [Appointment.Status.CONFIRMED, Appointment.Status.COMPLETED],
    })


@login_required
def my_appointments(request):
    user = request.user
    if user.is_patient():
        appointments = Appointment.objects.filter(patient=user)
    elif user.is_doctor():
        appointments = Appointment.objects.filter(doctor=user.doctor_profile)
    elif user.is_admin_user():
        appointments = Appointment.objects.all()
    else:
        appointments = Appointment.objects.none()

    appointments = appointments.select_related('doctor__user', 'patient', 'specialty')
    form = AppointmentFilterForm(request.GET or None)
    if form.is_valid():
        status = form.cleaned_data.get('status')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        if status:
            appointments = appointments.filter(status=status)
        if date_from:
            appointments = appointments.filter(date__gte=date_from)
        if date_to:
            appointments = appointments.filter(date__lte=date_to)

    return render(request, 'appointments/my_appointments.html', {'appointments': appointments, 'filter_form': form})


@login_required
def cancel_appointment(request, pk):
    appointment = _appointment_for_user_or_403(request, pk)
    allowed = request.user.is_admin_user() or appointment.patient_id == request.user.id or appointment.doctor.user_id == request.user.id
    if not allowed:
        raise PermissionDenied('Accès refusé.')
    if request.method == 'POST':
        if appointment.can_be_cancelled:
            appointment.status = Appointment.Status.CANCELLED
            appointment.save(update_fields=['status', 'updated_at'])
            messages.success(request, 'Rendez-vous annulé.')
        else:
            messages.error(request, 'Ce rendez-vous ne peut plus être annulé.')
    return redirect('appointments:detail', pk=appointment.pk)


@login_required
def reschedule_appointment(request, pk):
    appointment = _appointment_for_user_or_403(request, pk)
    if not request.user.is_patient() or appointment.patient_id != request.user.id:
        raise PermissionDenied('Seul le patient concerné peut modifier ce rendez-vous.')
    if not appointment.can_be_rescheduled:
        messages.error(request, 'Ce rendez-vous ne peut plus être modifié.')
        return redirect('appointments:detail', pk=appointment.pk)

    selected_date = _parse_date(request.GET.get('date'))
    selected_time = _parse_time(request.POST.get('selected_time') or request.GET.get('time'))
    slots = generate_slots_for_doctor(appointment.doctor, selected_date)
    if selected_date == appointment.date:
        slots = sorted(set(slots + [appointment.time]))

    if request.method == 'POST':
        if not selected_time or selected_time not in slots:
            messages.error(request, 'Veuillez choisir un créneau disponible.')
        else:
            appointment.date = selected_date
            appointment.time = selected_time
            try:
                appointment.full_clean()
                appointment.save(update_fields=['date', 'time', 'updated_at'])
                messages.success(request, 'Rendez-vous modifié avec succès.')
                return redirect('appointments:detail', pk=appointment.pk)
            except ValidationError as exc:
                messages.error(request, ' '.join(exc.messages) if hasattr(exc, 'messages') else str(exc))

    return render(request, 'appointments/reschedule.html', {'appointment': appointment, 'slots': slots, 'selected_date': selected_date})


@login_required
def confirm_appointment(request, pk):
    appointment = _appointment_for_user_or_403(request, pk)
    if not request.user.is_doctor() or appointment.doctor.user_id != request.user.id:
        raise PermissionDenied('Accès refusé.')
    if request.method == 'POST' and appointment.status == Appointment.Status.PENDING:
        appointment.status = Appointment.Status.CONFIRMED
        appointment.save(update_fields=['status', 'updated_at'])
        messages.success(request, 'Rendez-vous confirmé.')
    return redirect('appointments:detail', pk=appointment.pk)


@login_required
def complete_appointment(request, pk):
    appointment = _appointment_for_user_or_403(request, pk)
    if not request.user.is_doctor() or appointment.doctor.user_id != request.user.id:
        raise PermissionDenied('Accès refusé.')
    if request.method == 'POST' and appointment.status in [Appointment.Status.CONFIRMED, Appointment.Status.PENDING]:
        appointment.status = Appointment.Status.COMPLETED
        appointment.save(update_fields=['status', 'updated_at'])
        messages.success(request, 'Rendez-vous marqué comme terminé.')
    return redirect('appointments:detail', pk=appointment.pk)


@login_required
def mark_no_show(request, pk):
    appointment = _appointment_for_user_or_403(request, pk)
    if not request.user.is_doctor() or appointment.doctor.user_id != request.user.id:
        raise PermissionDenied('Accès refusé.')
    if request.method == 'POST' and appointment.status in [Appointment.Status.CONFIRMED, Appointment.Status.PENDING]:
        appointment.status = Appointment.Status.NO_SHOW
        appointment.save(update_fields=['status', 'updated_at'])
        messages.success(request, 'Rendez-vous marqué comme absent.')
    return redirect('appointments:detail', pk=appointment.pk)


@login_required
def add_consultation_summary(request, pk):
    appointment = _appointment_for_user_or_403(request, pk)
    if not request.user.is_doctor() or appointment.doctor.user_id != request.user.id:
        raise PermissionDenied('Accès refusé.')
    consultation = getattr(appointment, 'consultation', None)
    if request.method == 'POST':
        form = ConsultationForm(request.POST, instance=consultation)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.appointment = appointment
            obj.save()
            messages.success(request, 'Résumé administratif enregistré.')
            return redirect('appointments:detail', pk=appointment.pk)
    else:
        form = ConsultationForm(instance=consultation)
    return render(request, 'appointments/consultation_form.html', {'form': form, 'appointment': appointment})


@login_required
def add_review(request, pk):
    appointment = _appointment_for_user_or_403(request, pk)
    if not request.user.is_patient() or appointment.patient_id != request.user.id:
        raise PermissionDenied('Accès refusé.')
    if appointment.status != Appointment.Status.COMPLETED or hasattr(appointment, 'review'):
        messages.error(request, 'Vous ne pouvez donner un avis qu’après un rendez-vous terminé, et une seule fois.')
        return redirect('appointments:detail', pk=appointment.pk)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.appointment = appointment
            review.save()
            messages.success(request, 'Merci pour votre avis.')
            return redirect('appointments:detail', pk=appointment.pk)
    else:
        form = ReviewForm()
    return render(request, 'appointments/review_form.html', {'form': form, 'appointment': appointment})


@login_required
def get_slots_ajax(request, doctor_id):
    doctor = get_object_or_404(Doctor, pk=doctor_id, is_active=True)
    selected_date = _parse_date(request.GET.get('date'))
    slots = generate_slots_for_doctor(doctor, selected_date)
    return JsonResponse({'slots': [slot.strftime('%H:%M') for slot in slots]})

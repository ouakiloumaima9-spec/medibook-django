from functools import wraps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from .forms import AvailabilityForm, TimeOffForm
from .models import Availability, TimeOff


def doctor_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_doctor():
            return HttpResponseForbidden('Accès réservé aux médecins.')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
@doctor_required
def manage_availabilities(request):
    doctor = request.user.doctor_profile
    if request.method == 'POST':
        form = AvailabilityForm(request.POST)
        if form.is_valid():
            availability = form.save(commit=False)
            availability.doctor = doctor
            availability.save()
            messages.success(request, 'Disponibilité ajoutée.')
            return redirect('schedules:manage')
    else:
        form = AvailabilityForm()

    return render(request, 'schedules/manage.html', {
        'availabilities': doctor.availabilities.all(),
        'time_offs': doctor.time_offs.all(),
        'form': form,
    })


@login_required
@doctor_required
def delete_availability(request, pk):
    availability = get_object_or_404(Availability, pk=pk, doctor=request.user.doctor_profile)
    if request.method == 'POST':
        availability.delete()
        messages.success(request, 'Disponibilité supprimée.')
    return redirect('schedules:manage')


@login_required
@doctor_required
def add_timeoff(request):
    if request.method == 'POST':
        form = TimeOffForm(request.POST)
        if form.is_valid():
            timeoff = form.save(commit=False)
            timeoff.doctor = request.user.doctor_profile
            timeoff.save()
            messages.success(request, 'Période d’indisponibilité ajoutée.')
            return redirect('schedules:manage')
    else:
        form = TimeOffForm()
    return render(request, 'schedules/timeoff_form.html', {'form': form})


@login_required
@doctor_required
def delete_timeoff(request, pk):
    timeoff = get_object_or_404(TimeOff, pk=pk, doctor=request.user.doctor_profile)
    if request.method == 'POST':
        timeoff.delete()
        messages.success(request, 'Indisponibilité supprimée.')
    return redirect('schedules:manage')

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from .forms import DoctorProfileForm
from .models import Doctor, Specialty


def doctor_list(request):
    query = request.GET.get('q', '').strip()
    specialty_id = request.GET.get('specialty', '').strip()
    city = request.GET.get('city', '').strip()
    doctors = Doctor.objects.filter(is_active=True).select_related('user').prefetch_related('specialties')

    if query:
        doctors = doctors.filter(
            Q(user__first_name__icontains=query)
            | Q(user__last_name__icontains=query)
            | Q(specialties__name__icontains=query)
            | Q(bio__icontains=query)
        ).distinct()
    if specialty_id:
        doctors = doctors.filter(specialties__id=specialty_id)
    if city:
        doctors = doctors.filter(city__icontains=city)

    return render(request, 'doctors/doctor_list.html', {
        'doctors': doctors,
        'specialties': Specialty.objects.filter(is_active=True),
        'cities': Doctor.objects.filter(is_active=True).values_list('city', flat=True).distinct().order_by('city'),
        'query': query,
        'selected_specialty': specialty_id,
        'selected_city': city,
    })


def doctor_detail(request, pk):
    doctor = get_object_or_404(
        Doctor.objects.select_related('user').prefetch_related('specialties', 'availabilities'),
        pk=pk,
        is_active=True,
    )
    reviews = doctor.appointments.filter(review__isnull=False).select_related('patient', 'review').order_by('-review__created_at')[:5]
    return render(request, 'doctors/doctor_detail.html', {'doctor': doctor, 'reviews': reviews})


def specialty_list(request):
    return render(request, 'doctors/specialty_list.html', {'specialties': Specialty.objects.filter(is_active=True)})


@login_required
def my_doctor_profile(request):
    if not request.user.is_doctor():
        return HttpResponseForbidden('Accès réservé aux médecins.')
    doctor = request.user.doctor_profile
    if request.method == 'POST':
        form = DoctorProfileForm(request.POST, instance=doctor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil professionnel mis à jour.')
            return redirect('doctors:my_profile')
    else:
        form = DoctorProfileForm(instance=doctor)
    return render(request, 'doctors/my_profile.html', {'form': form, 'doctor': doctor})

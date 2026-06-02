from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from .forms import LoginForm, PatientProfileForm, PatientSignUpForm, ProfileUpdateForm
from .models import PatientProfile


def signup_view(request):
    if request.method == 'POST':
        form = PatientSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Compte créé avec succès. Bienvenue sur MediBook.')
            return redirect('dashboard:home')
    else:
        form = PatientSignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, 'Connexion réussie.')
            return redirect('dashboard:home')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Vous êtes déconnecté.')
    return redirect('accounts:login')


@login_required
def profile_view(request):
    user = request.user
    patient_profile = None
    if user.is_patient():
        patient_profile, _ = PatientProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        u_form = ProfileUpdateForm(request.POST, request.FILES, instance=user)
        p_form = PatientProfileForm(request.POST, instance=patient_profile) if patient_profile else None
        if u_form.is_valid() and (p_form is None or p_form.is_valid()):
            u_form.save()
            if p_form:
                p_form.save()
            messages.success(request, 'Profil mis à jour.')
            return redirect('accounts:profile')
    else:
        u_form = ProfileUpdateForm(instance=user)
        p_form = PatientProfileForm(instance=patient_profile) if patient_profile else None

    return render(request, 'accounts/profile.html', {'u_form': u_form, 'p_form': p_form})

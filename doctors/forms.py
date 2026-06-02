from django import forms
from django.contrib.auth.password_validation import validate_password
from .models import Doctor, Specialty
from accounts.models import User


class DoctorProfileForm(forms.ModelForm):
    """Formulaire d'édition du profil médecin (utilisé par le médecin lui-même)."""
    class Meta:
        model = Doctor
        fields = ['specialties', 'license_number', 'bio', 'years_of_experience',
                  'consultation_fee', 'office_address', 'city', 'languages', 'is_active']
        widgets = {
            'specialties': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name not in ['specialties', 'bio']:
                css = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'
                field.widget.attrs.setdefault('class', css)


class AdminAddDoctorForm(forms.Form):
    """
    Formulaire d'ajout d'un médecin par l'administrateur.
    Crée le compte User (rôle DOCTOR) + le profil Doctor en une seule étape.
    """
    # ── Informations du compte ────────────────────────────────────────
    first_name = forms.CharField(
        max_length=100, label='Prénom',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'})
    )
    last_name = forms.CharField(
        max_length=100, label='Nom',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom'})
    )
    username = forms.CharField(
        max_length=150, label="Nom d'utilisateur",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'username'})
    )
    email = forms.EmailField(
        label='Email professionnel',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@exemple.ma'})
    )
    phone = forms.CharField(
        max_length=20, required=False, label='Téléphone',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+212 6XX XXX XXX'})
    )
    password = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        validators=[validate_password],
        help_text='8 caractères minimum.'
    )
    password_confirm = forms.CharField(
        label='Confirmer le mot de passe',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    # ── Informations professionnelles ─────────────────────────────────
    specialties = forms.ModelMultipleChoiceField(
        queryset=Specialty.objects.filter(is_active=True),
        label='Spécialités',
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': '5'}),
        help_text='Maintenir Ctrl pour sélectionner plusieurs spécialités.'
    )
    license_number = forms.CharField(
        max_length=50, label="N° d'ordre des médecins",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex. 12345/C'})
    )
    bio = forms.CharField(
        required=False, label='Biographie / Description',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3,
                                     'placeholder': 'Présentation professionnelle...'})
    )
    years_of_experience = forms.IntegerField(
        min_value=0, max_value=60, initial=0, label="Années d'expérience",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    consultation_fee = forms.DecimalField(
        max_digits=8, decimal_places=2, initial=200.00,
        label='Honoraires (MAD)',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '50'})
    )
    office_address = forms.CharField(
        max_length=255, label='Adresse du cabinet',
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'placeholder': 'Adresse complète du cabinet'})
    )
    city = forms.CharField(
        max_length=100, initial='Casablanca', label='Ville',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    languages = forms.CharField(
        max_length=150, required=False,
        initial='Arabe, Français', label='Langues parlées',
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'placeholder': 'Ex. Arabe, Français, Anglais'})
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Ce nom d'utilisateur est déjà pris.")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Un compte avec cet email existe déjà.")
        return email

    def clean_license_number(self):
        license_number = self.cleaned_data['license_number']
        if Doctor.objects.filter(license_number=license_number).exists():
            raise forms.ValidationError("Ce numéro d'ordre est déjà enregistré.")
        return license_number

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', 'Les mots de passe ne correspondent pas.')
        return cleaned_data

    def save(self):
        """Crée le User (DOCTOR) + le Doctor en une transaction."""
        from django.db import transaction
        data = self.cleaned_data
        with transaction.atomic():
            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                phone=data.get('phone', ''),
                role=User.Role.DOCTOR,
            )
            doctor = Doctor.objects.create(
                user=user,
                license_number=data['license_number'],
                bio=data.get('bio', ''),
                years_of_experience=data['years_of_experience'],
                consultation_fee=data['consultation_fee'],
                office_address=data['office_address'],
                city=data['city'],
                languages=data.get('languages', 'Arabe, Français'),
                is_active=True,
            )
            doctor.specialties.set(data['specialties'])
        return doctor


class AdminEditDoctorForm(forms.ModelForm):
    """Formulaire d'édition d'un médecin par l'admin (modifie aussi le User associé)."""
    first_name = forms.CharField(max_length=100, label='Prénom',
                                  widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=100, label='Nom',
                                 widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label='Email',
                              widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=20, required=False, label='Téléphone',
                             widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Doctor
        fields = ['specialties', 'license_number', 'bio', 'years_of_experience',
                  'consultation_fee', 'office_address', 'city', 'languages', 'is_active']
        widgets = {
            'specialties': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '5'}),
            'bio': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
            self.fields['phone'].initial = self.instance.user.phone
        for name, field in self.fields.items():
            if name not in ['specialties', 'bio', 'is_active']:
                field.widget.attrs.setdefault('class', 'form-control')

    def save(self, commit=True):
        doctor = super().save(commit=commit)
        user = doctor.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data.get('phone', '')
        user.save()
        return doctor
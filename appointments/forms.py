from django import forms
from .models import Appointment, Consultation, Review


class AppointmentBookingForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['reason']
        widgets = {
            'reason': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Décrivez brièvement le motif administratif de votre consultation...',
            })
        }


class AppointmentFilterForm(forms.Form):
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'Tous les statuts')] + list(Appointment.Status.choices),
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))


class ConsultationForm(forms.ModelForm):
    class Meta:
        model = Consultation
        fields = ['summary']
        widgets = {
            'summary': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Résumé administratif : présence, acte administratif, remarque organisationnelle...',
            })
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Avis optionnel sur le service'}),
        }

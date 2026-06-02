from django import forms
from .models import Availability, TimeOff


class AvailabilityForm(forms.ModelForm):
    class Meta:
        model = Availability
        fields = ['weekday', 'start_time', 'end_time', 'slot_duration_minutes', 'is_active']
        widgets = {
            'weekday': forms.Select(attrs={'class': 'form-select'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'slot_duration_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': 10, 'step': 5}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned = super().clean()
        start, end = cleaned.get('start_time'), cleaned.get('end_time')
        if start and end and start >= end:
            raise forms.ValidationError('L’heure de fin doit être après l’heure de début.')
        return cleaned


class TimeOffForm(forms.ModelForm):
    class Meta:
        model = TimeOff
        fields = ['start_date', 'end_date', 'reason']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'reason': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned = super().clean()
        start, end = cleaned.get('start_date'), cleaned.get('end_date')
        if start and end and start > end:
            raise forms.ValidationError('La date de fin doit être après la date de début.')
        return cleaned

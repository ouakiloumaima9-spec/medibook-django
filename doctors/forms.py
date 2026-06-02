from django import forms
from .models import Doctor


class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['specialties', 'license_number', 'bio', 'years_of_experience', 'consultation_fee', 'office_address', 'city', 'languages', 'is_active']
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

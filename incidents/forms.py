from django import forms

from .models import Incident


class IncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = [
            'title',
            'description',
            'priority',
            'status',
            'assigned_engineer',
            'resolution_notes',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter incident title',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describe the incident in detail',
            }),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'assigned_engineer': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Engineer name',
            }),
            'resolution_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Add resolution notes (optional)',
            }),
        }

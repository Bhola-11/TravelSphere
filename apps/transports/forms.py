"""
Transports Search and Filter Forms.
"""
from django import forms
from apps.destinations.models import City
from apps.core.constants import TransportTypeEnum

class TransportSearchForm(forms.Form):
    origin_city = forms.ModelChoiceField(queryset=City.objects.all(), required=False, empty_label='From City', widget=forms.Select(attrs={'class': 'form-select'}))
    destination_city = forms.ModelChoiceField(queryset=City.objects.all(), required=False, empty_label='To City', widget=forms.Select(attrs={'class': 'form-select'}))
    departure_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    transport_type = forms.ChoiceField(choices=[('', 'All Modes')] + TransportTypeEnum.choices, required=False, widget=forms.Select(attrs={'class': 'form-select'}))

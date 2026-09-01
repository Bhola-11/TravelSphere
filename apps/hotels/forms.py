"""
Hotels Search, Filter, and Room Availability Request Forms.
"""
from django import forms
from .models import HotelProperty, Amenity
from apps.destinations.models import City

class HotelSearchForm(forms.Form):
    q = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Hotel name, city, landmark...'}))
    city = forms.ModelChoiceField(queryset=City.objects.all(), required=False, empty_label='All Cities', widget=forms.Select(attrs={'class': 'form-select'}))
    check_in = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    check_out = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    min_stars = forms.ChoiceField(choices=[('', 'Any Rating'), ('3', '3+ Stars'), ('4', '4+ Stars'), ('5', '5 Stars Only')], required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    property_type = forms.ChoiceField(choices=[('', 'All Types'), ('HOTEL', 'Luxury Hotel'), ('RESORT', 'Resort'), ('BOUTIQUE', 'Boutique'), ('VILLA', 'Villa')], required=False, widget=forms.Select(attrs={'class': 'form-select'}))

"""
Tours Search, Filter, and Booking Inquiry Forms.
"""
from django import forms
from .models import TourCategory, TourPackage
from apps.destinations.models import Destination

class TourSearchFilterForm(forms.Form):
    q = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search tour name, destination, activities...'}))
    destination = forms.ModelChoiceField(queryset=Destination.objects.filter(is_active=True), required=False, empty_label='All Destinations', widget=forms.Select(attrs={'class': 'form-select'}))
    category = forms.ModelChoiceField(queryset=TourCategory.objects.all(), required=False, empty_label='All Categories', widget=forms.Select(attrs={'class': 'form-select'}))
    min_days = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Min Days'}))
    max_days = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Max Days'}))
    max_price = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Max Budget ($)'}))
    difficulty = forms.ChoiceField(choices=[('', 'Any Difficulty'), ('EASY', 'Easy'), ('MODERATE', 'Moderate'), ('STRENUOUS', 'Strenuous'), ('EXTREME', 'Extreme')], required=False, widget=forms.Select(attrs={'class': 'form-select'}))

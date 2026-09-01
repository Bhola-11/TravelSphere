"""
Destinations Search and Filtering Forms.
"""
from django import forms
from .models import DestinationCategory, Continent, Country

class DestinationFilterForm(forms.Form):
    q = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by destination, city or country...'}))
    continent = forms.ModelChoiceField(queryset=Continent.objects.all(), required=False, empty_label='All Continents', widget=forms.Select(attrs={'class': 'form-select'}))
    country = forms.ModelChoiceField(queryset=Country.objects.all(), required=False, empty_label='All Countries', widget=forms.Select(attrs={'class': 'form-select'}))
    category = forms.ModelChoiceField(queryset=DestinationCategory.objects.all(), required=False, empty_label='All Categories', widget=forms.Select(attrs={'class': 'form-select'}))
    duration = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Max Days (e.g. 7)'}))

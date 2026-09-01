"""
Bookings Checkout and Passenger Details Forms.
"""
from django import forms
from .models import BookingOrder, PassengerDetail

class CheckoutBillingForm(forms.Form):
    name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email for Confirmation'}))
    phone = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Phone with Country Code'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Billing Street Address'}))
    special_requests = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Special dietary, accessibility or room requests...'}))

class PassengerDetailForm(forms.ModelForm):
    class Meta:
        model = PassengerDetail
        fields = ('title', 'first_name', 'last_name', 'date_of_birth', 'gender', 'passport_number', 'passport_country', 'passport_expiry', 'meal_preference')
        widgets = {
            'title': forms.Select(attrs={'class': 'form-select'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name as in Passport'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'passport_number': forms.TextInput(attrs={'class': 'form-control'}),
            'passport_country': forms.TextInput(attrs={'class': 'form-control'}),
            'passport_expiry': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'meal_preference': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Vegetarian, Halal, Kosher'}),
        }

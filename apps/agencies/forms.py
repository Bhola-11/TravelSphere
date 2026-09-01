"""
Agencies Forms: Partner Profile Setup & Staff Addition.
"""
from django import forms
from .models import Agency, AgencyStaff, AgencyCommissionPayout

class AgencyProfileForm(forms.ModelForm):
    class Meta:
        model = Agency
        fields = ('company_name', 'license_number', 'official_email', 'phone_number', 'address', 'website', 'logo')
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'license_number': forms.TextInput(attrs={'class': 'form-control'}),
            'official_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
        }

class PayoutRequestForm(forms.ModelForm):
    class Meta:
        model = AgencyCommissionPayout
        fields = ('amount', 'payout_method', 'bank_account_info')
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Amount in USD'}),
            'payout_method': forms.Select(attrs={'class': 'form-select'}, choices=[('BANK_WIRE', 'Bank Wire Transfer'), ('PAYPAL', 'PayPal'), ('STRIPE_CONNECT', 'Stripe Connect')]),
            'bank_account_info': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'IBAN, SWIFT / BIC, Account Holder Name, Bank Name'}),
        }

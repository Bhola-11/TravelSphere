"""
Payments Forms: Payment Method Selection & Coupon Code Form.
"""
from django import forms
from apps.core.constants import PaymentMethod

class PaymentSelectionForm(forms.Form):
    payment_method = forms.ChoiceField(
        choices=PaymentMethod.choices,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    card_number = forms.CharField(max_length=19, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '•••• •••• •••• ••••'}))
    card_expiry = forms.CharField(max_length=7, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'MM/YY'}))
    card_cvv = forms.CharField(max_length=4, required=False, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'CVV'}))

class ApplyCouponForm(forms.Form):
    coupon_code = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Promo Code'}))

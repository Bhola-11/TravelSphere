"""
Authentication, Registration, Profile, and Verification Forms.
"""
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from .models import CustomerProfile, AgencyProfile, UserAddress, KYCDocument
from apps.core.constants import UserRole

User = get_user_model()

class CustomerRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com'}))
    phone_number = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 (555) 000-0000'}))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = UserRole.CUSTOMER
        if commit:
            user.save()
            CustomerProfile.objects.get_or_create(user=user)
        return user

class AgencyRegistrationForm(UserCreationForm):
    company_name = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Agency Company Name'}))
    trade_license_number = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Trade License No.'}))
    first_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Person First Name'}))
    last_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Person Last Name'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'agency@company.com'}))
    phone_number = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 (555) 123-4567'}))
    office_address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Headquarters Office Address'}))

    class Meta:
        model = User
        fields = ('company_name', 'trade_license_number', 'first_name', 'last_name', 'email', 'phone_number', 'office_address')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = UserRole.AGENCY_ADMIN
        if commit:
            user.save()
            AgencyProfile.objects.create(
                user=user,
                company_name=self.cleaned_data['company_name'],
                trade_license_number=self.cleaned_data['trade_license_number'],
                official_email=user.email,
                office_phone=user.phone_number,
                office_address=self.cleaned_data['office_address']
            )
        return user

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email address or Phone'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

class CustomerProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomerProfile
        fields = ('date_of_birth', 'gender', 'nationality', 'passport_number', 'passport_expiry', 'emergency_contact_name', 'emergency_contact_phone', 'dietary_preferences', 'preferred_currency')
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'nationality': forms.TextInput(attrs={'class': 'form-control'}),
            'passport_number': forms.TextInput(attrs={'class': 'form-control'}),
            'passport_expiry': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'dietary_preferences': forms.TextInput(attrs={'class': 'form-control'}),
            'preferred_currency': forms.Select(attrs={'class': 'form-select'}),
        }

class UserInfoUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone_number', 'avatar')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }

class AddressForm(forms.ModelForm):
    class Meta:
        model = UserAddress
        exclude = ('user',)
        widgets = {
            'address_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Home, Office'}),
            'recipient_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'street_address': forms.TextInput(attrs={'class': 'form-control'}),
            'apartment_suite': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state_province': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class KYCUploadForm(forms.ModelForm):
    class Meta:
        model = KYCDocument
        fields = ('document_type', 'document_number', 'file')
        widgets = {
            'document_type': forms.Select(attrs={'class': 'form-select'}),
            'document_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Document Identification Number'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }

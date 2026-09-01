"""
Agencies App Models: Partner Onboarding, Staff Rosters, Tiered Commissions & B2B Packages.
"""
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.core.models import AuditableModel, SluggedModel, TimeStampedModel

class Agency(AuditableModel, SluggedModel):
    """Enterprise Travel Agency Partner Profile."""
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_agency')
    company_name = models.CharField(max_length=200, unique=True)
    license_number = models.CharField(max_length=100, unique=True)
    tax_id = models.CharField(max_length=100, blank=True)
    
    logo = models.ImageField(upload_to='agencies/logos/', null=True, blank=True)
    official_email = models.EmailField()
    phone_number = models.CharField(max_length=30)
    address = models.TextField()
    website = models.URLField(blank=True)
    
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('10.00'), help_text="Commission % on packages sold")
    wallet_balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_revenue_generated = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    rating_average = models.DecimalField(max_digits=3, decimal_places=2, default=5.00)

    class Meta:
        verbose_name_plural = "Agencies"
        ordering = ['-is_verified', 'company_name']

    def __str__(self):
        return f"{self.company_name} ({self.license_number})"

class AgencyStaff(TimeStampedModel):
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='staff_members')
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='agency_staff_profile')
    role_title = models.CharField(max_length=100, default='Travel Consultant')
    can_manage_packages = models.BooleanField(default=True)
    can_view_finance = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.role_title}) - {self.agency.company_name}"

class AgencyCommissionPayout(TimeStampedModel):
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='payouts')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payout_method = models.CharField(max_length=50, default='BANK_WIRE')
    bank_account_info = models.TextField()
    status = models.CharField(max_length=30, choices=[
        ('REQUESTED', 'Requested'),
        ('PROCESSING', 'Processing Transfer'),
        ('COMPLETED', 'Dispatched / Completed'),
        ('REJECTED', 'Rejected'),
    ], default='REQUESTED')
    reference_number = models.CharField(max_length=100, blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Payout of ${self.amount} to {self.agency.company_name} [{self.status}]"

"""
Accounts Models: Custom User Model, Multi-tier Roles, Detailed Profiles, KYC & Address Management.
"""
import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel, UUIDModel, SoftDeleteModel
from apps.core.constants import UserRole, KYCStatus

class TravelSphereUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('An email address is required.'))
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', UserRole.SUPER_ADMIN)
        extra_fields.setdefault('is_verified', True)
        extra_fields.setdefault('kyc_status', KYCStatus.VERIFIED)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)

class TravelSphereUser(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    """Unified Custom User model for Customers, Travel Agents, Hotel & Transport Partners, and Admins."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email address'), unique=True, db_index=True)
    first_name = models.CharField(_('first name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150)
    phone_number = models.CharField(_('phone number'), max_length=30, blank=True, null=True, db_index=True)
    
    role = models.CharField(
        _('user role'),
        max_length=30,
        choices=UserRole.choices,
        default=UserRole.CUSTOMER,
        db_index=True
    )
    
    avatar = models.ImageField(upload_to='avatars/%Y/%m/', null=True, blank=True)
    is_verified = models.BooleanField(_('verified status'), default=False)
    kyc_status = models.CharField(
        _('KYC status'),
        max_length=20,
        choices=KYCStatus.choices,
        default=KYCStatus.UNVERIFIED
    )
    
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff status'), default=False)
    
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = TravelSphereUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.get_full_name()} ({self.email}) [{self.role}]"

    def get_full_name(self):
        full = f"{self.first_name} {self.last_name}".strip()
        return full or self.email

    def get_short_name(self):
        return self.first_name or self.email

    @property
    def is_customer(self):
        return self.role == UserRole.CUSTOMER

    @property
    def is_agency(self):
        return self.role in [UserRole.AGENCY_ADMIN, UserRole.AGENT]

    @property
    def is_hotel_manager(self):
        return self.role == UserRole.HOTEL_MANAGER

    @property
    def is_transport_manager(self):
        return self.role == UserRole.TRANSPORT_MANAGER

    @property
    def is_admin(self):
        return self.role == UserRole.SUPER_ADMIN or self.is_superuser

class CustomerProfile(TimeStampedModel):
    """Customer-specific travel preferences, passport data, and loyalty stats."""
    user = models.OneToOneField(TravelSphereUser, on_delete=models.CASCADE, related_name='customer_profile')
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    passport_number = models.CharField(max_length=50, blank=True)
    passport_expiry = models.DateField(null=True, blank=True)
    emergency_contact_name = models.CharField(max_length=150, blank=True)
    emergency_contact_phone = models.CharField(max_length=30, blank=True)
    dietary_preferences = models.CharField(max_length=255, blank=True)
    loyalty_points = models.PositiveIntegerField(default=0)
    preferred_currency = models.CharField(max_length=3, default='USD')

    def __str__(self):
        return f"Customer Profile: {self.user.get_full_name()}"

class AgencyProfile(TimeStampedModel):
    """Corporate Travel Agency Partner details, licensing, and commission settings."""
    user = models.OneToOneField(TravelSphereUser, on_delete=models.CASCADE, related_name='agency_admin_profile')
    company_name = models.CharField(max_length=255)
    trade_license_number = models.CharField(max_length=100, unique=True)
    tax_id = models.CharField(max_length=100, blank=True)
    company_website = models.URLField(blank=True)
    official_email = models.EmailField()
    office_phone = models.CharField(max_length=30)
    office_address = models.TextField()
    commission_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    is_approved = models.BooleanField(default=False)
    approved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Agency: {self.company_name}"

class UserAddress(TimeStampedModel):
    """Reusable user addresses for invoicing, dispatch, and emergency logs."""
    user = models.ForeignKey(TravelSphereUser, on_delete=models.CASCADE, related_name='addresses')
    address_title = models.CharField(max_length=50, default='Home')
    recipient_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=30)
    street_address = models.CharField(max_length=255)
    apartment_suite = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100)
    state_province = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=30)
    country = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "User Addresses"

    def save(self, *args, **kwargs):
        if self.is_default:
            UserAddress.objects.filter(user=self.user).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.address_title} - {self.street_address}, {self.city}"

class KYCDocument(TimeStampedModel):
    """Identity and corporate verification files."""
    user = models.ForeignKey(TravelSphereUser, on_delete=models.CASCADE, related_name='kyc_documents')
    document_type = models.CharField(max_length=50, choices=[
        ('PASSPORT', 'Passport / Government ID'),
        ('DRIVING_LICENSE', 'Driver License'),
        ('TRADE_LICENSE', 'Agency Trade License'),
        ('TAX_CERTIFICATE', 'Tax Exemption Certificate'),
        ('UTILITY_BILL', 'Proof of Address (Utility Bill)'),
    ])
    document_number = models.CharField(max_length=100)
    file = models.FileField(upload_to='kyc_documents/%Y/%m/')
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        TravelSphereUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='verified_kyc_docs'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    def __str__(self):
        return f"{self.get_document_type_display()} for {self.user.email}"

class UserActivityLog(TimeStampedModel):
    """Granular user action history (login, profile updates, bookings)."""
    user = models.ForeignKey(TravelSphereUser, on_delete=models.CASCADE, related_name='account_activity_logs')
    activity_type = models.CharField(max_length=100)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.activity_type} at {self.created_at}"

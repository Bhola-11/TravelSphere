"""
Core Abstract Models, Global Managers, Audit Trail, and System Configuration.
"""
import uuid
from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.conf import settings
from .constants import CurrencyCode, UserRole

class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True, is_deleted=False)

class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class TimeStampedModel(models.Model):
    """Abstract model providing self-updating created_at and updated_at fields."""
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class UUIDModel(models.Model):
    """Abstract model providing a secure UUID primary key."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True

class SoftDeleteModel(models.Model):
    """Abstract model supporting soft-deletion."""
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'deleted_at'])

    class Meta:
        abstract = True

class AuditableModel(TimeStampedModel, SoftDeleteModel):
    """Base model combining UUID, timestamps, active state, and soft deletion."""
    is_active = models.BooleanField(default=True, db_index=True)

    objects = ActiveManager()
    all_with_inactive = SoftDeleteManager()
    raw_objects = models.Manager()

    class Meta:
        abstract = True

class SluggedModel(models.Model):
    """Abstract model providing automatic unique slug generation."""
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=300, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            unique_slug = base_slug
            num = 1
            model_class = self.__class__
            while model_class.objects.filter(slug=unique_slug).exclude(pk=self.pk).exists():
                unique_slug = f"{base_slug}-{num}"
                num += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

    class Meta:
        abstract = True

class SystemConfiguration(TimeStampedModel):
    """Global system dynamic settings stored in DB with Redis cache layer."""
    site_name = models.CharField(max_length=150, default="TravelSphere")
    tagline = models.CharField(max_length=255, default="Enterprise Global Travel & Tour Management")
    contact_email = models.EmailField(default="support@travelsphere.com")
    contact_phone = models.CharField(max_length=30, default="+1 (800) 555-SPHERE")
    support_address = models.TextField(default="742 Evergreen Terrace, Suite 500, San Francisco, CA")
    
    # Financial Configuration
    default_currency = models.CharField(max_length=3, choices=CurrencyCode.choices, default=CurrencyCode.USD)
    platform_fee_percent = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("3.50"))
    agency_commission_percent = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("10.00"))
    tax_rate_percent = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("5.00"))
    
    # System Controls
    maintenance_mode = models.BooleanField(default=False)
    allow_agency_registrations = models.BooleanField(default=True)
    require_kyc_for_booking = models.BooleanField(default=False)
    enable_ai_recommendations = models.BooleanField(default=True)
    enable_dynamic_pricing = models.BooleanField(default=True)
    
    # Notification & Rate Limits
    max_booking_passengers = models.PositiveIntegerField(default=20)
    cancellation_deadline_hours = models.PositiveIntegerField(default=48)

    class Meta:
        verbose_name = "System Configuration"
        verbose_name_plural = "System Configurations"

    def __str__(self):
        return f"{self.site_name} Configuration (Updated: {self.updated_at.strftime('%Y-%m-%d')})"

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(id=1)
        return obj

class CurrencyExchangeRate(TimeStampedModel):
    """Real-time & cached multi-currency conversion table."""
    base_currency = models.CharField(max_length=3, choices=CurrencyCode.choices, default=CurrencyCode.USD)
    target_currency = models.CharField(max_length=3, choices=CurrencyCode.choices)
    rate = models.DecimalField(max_digits=12, decimal_places=6)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('base_currency', 'target_currency')
        verbose_name = "Currency Exchange Rate"
        verbose_name_plural = "Currency Exchange Rates"

    def __str__(self):
        return f"1 {self.base_currency} = {self.rate} {self.target_currency}"

class AuditLog(TimeStampedModel):
    """High-fidelity system-wide action audit trail."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='core_audit_logs')
    action = models.CharField(max_length=100, db_index=True)
    entity_type = models.CharField(max_length=100, db_index=True)
    entity_id = models.CharField(max_length=100, blank=True, null=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    changes_json = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['entity_type', 'entity_id']),
            models.Index(fields=['action', 'created_at']),
        ]

    def __str__(self):
        return f"[{self.created_at.strftime('%Y-%m-%d %H:%M:%S')}] {self.action} on {self.entity_type} by {self.user}"

class ContactInquiry(TimeStampedModel):
    """Public customer and partner contact support tickets."""
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    resolution_notes = models.TextField(blank=True)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Inquiry from {self.full_name} ({self.subject})"

"""
Payments App Models: Gateways, Transactions, Invoices, Coupons, Tax Rules & Refunds.
"""
import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.core.models import AuditableModel, UUIDModel, TimeStampedModel
from apps.core.constants import PaymentStatus, PaymentMethod

class Coupon(TimeStampedModel):
    """Promotional promo code engine with usage limits & date constraints."""
    code = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('10.00'))
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('100.00'))
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('50.00'))
    valid_from = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField()
    max_usages = models.PositiveIntegerField(default=500)
    current_usages = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def is_valid_for(self, amount: Decimal):
        now = timezone.now()
        if not self.is_active:
            return False, "Coupon is disabled."
        if now < self.valid_from or now > self.valid_until:
            return False, "Coupon has expired."
        if self.current_usages >= self.max_usages:
            return False, "Coupon usage limit reached."
        if amount < self.min_order_amount:
            return False, f"Minimum order amount of ${self.min_order_amount} required."
        return True, "Valid"

    def calculate_discount(self, amount: Decimal) -> Decimal:
        discount = (amount * self.discount_percentage / Decimal('100.00'))
        return min(discount, self.max_discount_amount).quantize(Decimal('0.01'))

    def __str__(self):
        return f"{self.code} ({self.discount_percentage}% off)"

class TaxRate(TimeStampedModel):
    """Regional & Tourism Tax Rates (GST, VAT, Tourism Surcharge)."""
    name = models.CharField(max_length=100)
    country_code = models.CharField(max_length=2, default='US')
    rate_percent = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('5.00'))
    is_compound = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.rate_percent}% ({self.country_code})"

class PaymentTransaction(AuditableModel, UUIDModel):
    """Immutable ledger of payment attempts and gateway callbacks."""
    booking = models.ForeignKey('bookings.BookingOrder', on_delete=models.CASCADE, related_name='payments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payment_transactions')
    
    transaction_reference = models.CharField(max_length=100, unique=True, db_index=True)
    gateway_reference = models.CharField(max_length=150, blank=True, null=True)
    
    payment_method = models.CharField(max_length=30, choices=PaymentMethod.choices, default=PaymentMethod.STRIPE)
    status = models.CharField(max_length=30, choices=PaymentStatus.choices, default=PaymentStatus.PENDING, db_index=True)
    
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    gateway_response = models.JSONField(default=dict, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    failure_reason = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Txn #{self.transaction_reference} - {self.status} (${self.amount})"

class Invoice(TimeStampedModel, UUIDModel):
    """Formal PDF/Tax Invoice generated for confirmed travel bookings."""
    booking = models.OneToOneField('bookings.BookingOrder', on_delete=models.CASCADE, related_name='invoice')
    invoice_number = models.CharField(max_length=50, unique=True)
    issued_date = models.DateField(default=timezone.now)
    due_date = models.DateField(default=timezone.now)
    
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    is_paid = models.BooleanField(default=False)
    paid_date = models.DateTimeField(null=True, blank=True)
    pdf_file = models.FileField(upload_to='invoices/%Y/%m/', null=True, blank=True)

    def __str__(self):
        return f"Invoice #{self.invoice_number} for Order #{self.booking.booking_reference}"

class RefundRequest(AuditableModel, UUIDModel):
    """Customer cancellation refund claims processed according to policy."""
    booking = models.ForeignKey('bookings.BookingOrder', on_delete=models.CASCADE, related_name='refund_requests')
    transaction = models.ForeignKey(PaymentTransaction, on_delete=models.SET_NULL, null=True, blank=True)
    
    requested_amount = models.DecimalField(max_digits=12, decimal_places=2)
    approved_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    cancellation_fee = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    status = models.CharField(max_length=30, choices=[
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved & Processing'),
        ('PROCESSED', 'Refund Dispatched'),
        ('REJECTED', 'Claim Rejected'),
    ], default='PENDING')
    
    reason = models.TextField()
    admin_notes = models.TextField(blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Refund for #{self.booking.booking_reference} [{self.status}]"

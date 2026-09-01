"""
Bookings App Models: Unified Cart, Booking Orders, Line Items, Passengers, Vouchers & State Transitions.
"""
import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.core.models import AuditableModel, UUIDModel, TimeStampedModel
from apps.core.constants import BookingStatus

class Cart(TimeStampedModel):
    """Session or User-bound shopping cart for multi-item travel reservations."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='active_cart')
    session_key = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart ({self.user.email if self.user else self.session_key})"

    @property
    def total_items_count(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        return sum(item.subtotal for item in self.items.all())

class CartItem(TimeStampedModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    item_type = models.CharField(max_length=30, choices=[
        ('TOUR', 'Tour Package'),
        ('HOTEL', 'Hotel Room Reservation'),
        ('TRANSPORT', 'Transport Ticket'),
        ('CUSTOM_PACKAGE', 'Custom Multi-City Bundle'),
    ])
    
    # Generic reference IDs
    tour_package = models.ForeignKey('tours.TourPackage', on_delete=models.SET_NULL, null=True, blank=True)
    room_type = models.ForeignKey('hotels.RoomType', on_delete=models.SET_NULL, null=True, blank=True)
    transport_schedule = models.ForeignKey('transports.TransportSchedule', on_delete=models.SET_NULL, null=True, blank=True)
    seat_class = models.ForeignKey('transports.SeatClass', on_delete=models.SET_NULL, null=True, blank=True)
    
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    
    adults_count = models.PositiveIntegerField(default=1)
    children_count = models.PositiveIntegerField(default=0)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    metadata = models.JSONField(default=dict, blank=True)

    @property
    def subtotal(self):
        return (self.unit_price * Decimal(str(self.quantity))).quantize(Decimal('0.01'))

    def __str__(self):
        return f"CartItem: {self.item_type} - ${self.subtotal}"

class BookingOrder(AuditableModel, UUIDModel):
    """Parent transaction entity covering a complete customer reservation."""
    booking_reference = models.CharField(max_length=30, unique=True, db_index=True)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    agency = models.ForeignKey('agencies.Agency', on_delete=models.SET_NULL, null=True, blank=True, related_name='agency_orders')
    
    status = models.CharField(max_length=30, choices=BookingStatus.choices, default=BookingStatus.PENDING_PAYMENT, db_index=True)
    
    # Financial breakdown
    currency = models.CharField(max_length=3, default='USD')
    subtotal_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    # Contact and Billing Snapshot
    billing_name = models.CharField(max_length=150)
    billing_email = models.EmailField()
    billing_phone = models.CharField(max_length=30)
    billing_address = models.TextField(blank=True)
    special_requests = models.TextField(blank=True)
    
    # Lifecycle Timestamps
    confirmed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.booking_reference} [{self.status}] - ${self.total_amount}"

    def generate_reference(self):
        import random, string
        suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"TS-{timezone.now().strftime('%Y%m')}-{suffix}"

    def save(self, *args, **kwargs):
        if not self.booking_reference:
            self.booking_reference = self.generate_reference()
        super().save(*args, **kwargs)

class BookingLineItem(TimeStampedModel):
    """Specific line items (e.g. Tour in Paris, 3 nights in Hotel, Flight to Rome)."""
    booking = models.ForeignKey(BookingOrder, on_delete=models.CASCADE, related_name='line_items')
    item_type = models.CharField(max_length=30, choices=[
        ('TOUR', 'Tour Package'),
        ('HOTEL', 'Hotel Room Reservation'),
        ('TRANSPORT', 'Transport Ticket'),
    ])
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    tour_package = models.ForeignKey('tours.TourPackage', on_delete=models.SET_NULL, null=True, blank=True)
    room_type = models.ForeignKey('hotels.RoomType', on_delete=models.SET_NULL, null=True, blank=True)
    transport_schedule = models.ForeignKey('transports.TransportSchedule', on_delete=models.SET_NULL, null=True, blank=True)
    seat_class = models.ForeignKey('transports.SeatClass', on_delete=models.SET_NULL, null=True, blank=True)
    
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    snapshot_data = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.title} (${self.total_price})"

class PassengerDetail(TimeStampedModel):
    """Passenger/Guest passport and personal info per booking line item."""
    booking = models.ForeignKey(BookingOrder, on_delete=models.CASCADE, related_name='passengers')
    line_item = models.ForeignKey(BookingLineItem, on_delete=models.SET_NULL, null=True, blank=True, related_name='passengers')
    
    title = models.CharField(max_length=10, choices=[('MR', 'Mr.'), ('MRS', 'Mrs.'), ('MS', 'Ms.'), ('MSTR', 'Master'), ('DR', 'Dr.')], default='MR')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], default='M')
    passport_number = models.CharField(max_length=50, blank=True)
    passport_country = models.CharField(max_length=100, blank=True)
    passport_expiry = models.DateField(null=True, blank=True)
    meal_preference = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.get_title_display()} {self.first_name} {self.last_name}"

class BookingStatusHistory(TimeStampedModel):
    """Audit track of booking status progressions."""
    booking = models.ForeignKey(BookingOrder, on_delete=models.CASCADE, related_name='status_history')
    old_status = models.CharField(max_length=30)
    new_status = models.CharField(max_length=30)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.booking.booking_reference}: {self.old_status} -> {self.new_status}"

class BookingVoucher(TimeStampedModel, UUIDModel):
    """Digital entry pass and e-ticket with validation barcode/QR."""
    booking = models.ForeignKey(BookingOrder, on_delete=models.CASCADE, related_name='vouchers')
    voucher_code = models.CharField(max_length=50, unique=True)
    qr_code_image = models.ImageField(upload_to='vouchers/qr/', null=True, blank=True)
    is_redeemed = models.BooleanField(default=False)
    redeemed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Voucher: {self.voucher_code} (Booking #{self.booking.booking_reference})"

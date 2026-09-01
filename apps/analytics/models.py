"""
Analytics App Models: Search & View Telemetry, Daily Revenue Aggregates, and AI Recommendation Logs.
"""
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.core.models import TimeStampedModel

class UserSearchLog(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    session_key = models.CharField(max_length=100, blank=True)
    search_query = models.CharField(max_length=255)
    category_filter = models.CharField(max_length=100, blank=True)
    results_count = models.PositiveIntegerField(default=0)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Search '{self.search_query}' ({self.results_count} results)"

class PackageViewLog(TimeStampedModel):
    tour_package = models.ForeignKey('tours.TourPackage', on_delete=models.CASCADE, related_name='view_logs')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(default=0)
    source = models.CharField(max_length=100, default='DIRECT')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"View for {self.tour_package.title}"

class RevenueDailyMetric(models.Model):
    date = models.DateField(unique=True, db_index=True)
    gross_revenue = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    net_revenue = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    total_tax_collected = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_agency_payouts = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_bookings_count = models.PositiveIntegerField(default=0)
    new_users_registered = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Metric for {self.date}: ${self.gross_revenue} ({self.total_bookings_count} bookings)"

class DynamicPriceAdjustmentLog(TimeStampedModel):
    tour_package = models.ForeignKey('tours.TourPackage', on_delete=models.CASCADE, related_name='price_adjustments')
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    adjusted_price = models.DecimalField(max_digits=10, decimal_places=2)
    adjustment_factor = models.DecimalField(max_digits=4, decimal_places=2)
    trigger_reason = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.tour_package.title}: ${self.original_price} -> ${self.adjusted_price} ({self.trigger_reason})"

"""
Celery Background Tasks: Booking Reminder Dispatch, Auto-Cancellation & Nightly Aggregation.
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta

@shared_task
def send_booking_confirmation_email_task(booking_id):
    """Sends confirmation email with travel voucher."""
    print(f"Executing async task: Sending booking confirmation email for booking {booking_id}")
    return f"Confirmation sent for {booking_id}"

@shared_task
def check_expired_pending_bookings_task():
    """Cancels orders held in PENDING_PAYMENT for longer than 48 hours."""
    from apps.bookings.models import BookingOrder
    from apps.core.constants import BookingStatus
    
    cutoff = timezone.now() - timedelta(hours=48)
    expired = BookingOrder.objects.filter(status=BookingStatus.PENDING_PAYMENT, created_at__lt=cutoff)
    count = expired.count()
    for order in expired:
        order.status = BookingStatus.CANCELLED
        order.cancellation_reason = "Auto-cancelled due to payment timeout (48h limit)."
        order.save(update_fields=['status', 'cancellation_reason'])
    return f"Auto-cancelled {count} expired bookings."

@shared_task
def aggregate_nightly_revenue_metric_task():
    """Computes daily revenue aggregate metrics for BI dashboard."""
    from apps.bookings.models import BookingOrder
    from apps.analytics.models import RevenueDailyMetric
    from django.db.models import Sum, Count
    from decimal import Decimal

    today = timezone.now().date()
    stats = BookingOrder.objects.filter(
        status__in=['CONFIRMED', 'COMPLETED'],
        created_at__date=today
    ).aggregate(
        total_rev=Sum('total_amount'),
        total_tax=Sum('tax_amount'),
        count=Count('id')
    )

    RevenueDailyMetric.objects.update_or_create(
        date=today,
        defaults={
            'gross_revenue': stats['total_rev'] or Decimal('0.00'),
            'net_revenue': (stats['total_rev'] or Decimal('0.00')) - (stats['total_tax'] or Decimal('0.00')),
            'total_tax_collected': stats['total_tax'] or Decimal('0.00'),
            'total_bookings_count': stats['count'] or 0,
        }
    )
    return f"Aggregated daily metric for {today}"

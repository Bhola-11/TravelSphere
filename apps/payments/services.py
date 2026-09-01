"""
Payments Service Layer: Gateway Processing, Invoicing, Tax Calculation & Refund Matrix.
"""
import uuid
from decimal import Decimal
from django.utils import timezone
from django.db import transaction
from .models import PaymentTransaction, Invoice, RefundRequest, TaxRate, Coupon
from apps.core.constants import PaymentStatus, BookingStatus

class TaxCalculationEngine:
    @staticmethod
    def calculate_taxes(subtotal: Decimal, country_code='US'):
        rates = TaxRate.objects.filter(country_code=country_code, is_active=True)
        total_tax_rate = Decimal('5.00') # Default baseline
        if rates.exists():
            total_tax_rate = sum(r.rate_percent for r in rates)
        
        tax_amount = (subtotal * total_tax_rate / Decimal('100.00')).quantize(Decimal('0.01'))
        return {
            'tax_rate_percent': total_tax_rate,
            'tax_amount': tax_amount
        }

class PaymentGatewayService:
    @staticmethod
    @transaction.atomic
    def process_payment(order, payment_method, user):
        txn_ref = f"TXN-{uuid.uuid4().hex[:10].upper()}"
        
        # Simulated Gateway Execution
        txn = PaymentTransaction.objects.create(
            booking=order,
            user=user,
            transaction_reference=txn_ref,
            gateway_reference=f"GW-{uuid.uuid4().hex[:12].upper()}",
            payment_method=payment_method,
            status=PaymentStatus.SUCCESS,
            amount=order.total_amount,
            currency=order.currency,
            paid_at=timezone.now(),
            gateway_response={'status': 'authorized', 'code': '200'}
        )

        # Update Order Status
        order.status = BookingStatus.CONFIRMED
        order.confirmed_at = timezone.now()
        order.save(update_fields=['status', 'confirmed_at'])

        # Generate Formal Invoice
        inv_num = f"INV-{order.booking_reference}"
        Invoice.objects.create(
            booking=order,
            invoice_number=inv_num,
            subtotal=order.subtotal_amount,
            tax_amount=order.tax_amount,
            discount_amount=order.discount_amount,
            total_amount=order.total_amount,
            is_paid=True,
            paid_date=timezone.now()
        )

        # Log history
        from apps.bookings.models import BookingStatusHistory
        BookingStatusHistory.objects.create(
            booking=order,
            old_status=BookingStatus.PENDING_PAYMENT,
            new_status=BookingStatus.CONFIRMED,
            changed_by=user,
            notes=f"Payment completed via {payment_method}. Txn: {txn_ref}"
        )

        return txn

"""
Agencies Service Layer: Commission Calculations, Sales Aggregation & Performance Metrics.
"""
from decimal import Decimal
from django.db.models import Sum, Count
from .models import Agency, AgencyCommissionPayout

class AgencyCommissionService:
    @staticmethod
    def calculate_commission(agency: Agency, booking_amount: Decimal) -> Decimal:
        return (booking_amount * agency.commission_rate / Decimal('100.00')).quantize(Decimal('0.01'))

    @staticmethod
    def record_sale(agency: Agency, booking_amount: Decimal):
        commission = AgencyCommissionService.calculate_commission(agency, booking_amount)
        agency.wallet_balance += commission
        agency.total_revenue_generated += booking_amount
        agency.save(update_fields=['wallet_balance', 'total_revenue_generated'])
        return commission

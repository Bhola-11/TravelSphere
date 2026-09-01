from django.contrib import admin
from .models import Coupon, TaxRate, PaymentTransaction, Invoice, RefundRequest

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_reference', 'booking', 'user', 'amount', 'currency', 'status', 'payment_method', 'created_at')
    list_filter = ('status', 'payment_method', 'currency')
    search_fields = ('transaction_reference', 'booking__booking_reference', 'user__email')

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'booking', 'total_amount', 'is_paid', 'issued_date')
    search_fields = ('invoice_number', 'booking__booking_reference')

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percentage', 'max_discount_amount', 'current_usages', 'max_usages', 'is_active', 'valid_until')
    list_filter = ('is_active',)
    search_fields = ('code', 'description')

admin.site.register(TaxRate)
admin.site.register(RefundRequest)

from django.contrib import admin
from .models import Cart, CartItem, BookingOrder, BookingLineItem, PassengerDetail, BookingStatusHistory, BookingVoucher

class BookingLineItemInline(admin.TabularInline):
    model = BookingLineItem
    extra = 0

class PassengerDetailInline(admin.TabularInline):
    model = PassengerDetail
    extra = 0

class BookingStatusHistoryInline(admin.TabularInline):
    model = BookingStatusHistory
    extra = 0
    readonly_fields = [f.name for f in BookingStatusHistory._meta.fields]

@admin.register(BookingOrder)
class BookingOrderAdmin(admin.ModelAdmin):
    list_display = ('booking_reference', 'customer', 'status', 'total_amount', 'currency', 'created_at')
    list_filter = ('status', 'currency', 'created_at')
    search_fields = ('booking_reference', 'customer__email', 'billing_name')
    inlines = [BookingLineItemInline, PassengerDetailInline, BookingStatusHistoryInline]

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'session_key', 'created_at')

admin.site.register(BookingVoucher)

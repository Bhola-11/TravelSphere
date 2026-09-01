from django.contrib import admin
from .models import Agency, AgencyStaff, AgencyCommissionPayout

class AgencyStaffInline(admin.TabularInline):
    model = AgencyStaff
    extra = 1

@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'license_number', 'official_email', 'commission_rate', 'wallet_balance', 'is_verified')
    list_filter = ('is_verified',)
    search_fields = ('company_name', 'license_number', 'official_email')
    prepopulated_fields = {'slug': ('company_name',)}
    inlines = [AgencyStaffInline]

@admin.register(AgencyCommissionPayout)
class AgencyCommissionPayoutAdmin(admin.ModelAdmin):
    list_display = ('agency', 'amount', 'payout_method', 'status', 'created_at')
    list_filter = ('status', 'payout_method')

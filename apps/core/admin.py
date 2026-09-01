from django.contrib import admin
from .models import SystemConfiguration, CurrencyExchangeRate, AuditLog, ContactInquiry

@admin.register(SystemConfiguration)
class SystemConfigurationAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'default_currency', 'platform_fee_percent', 'maintenance_mode', 'updated_at')

@admin.register(CurrencyExchangeRate)
class CurrencyExchangeRateAdmin(admin.ModelAdmin):
    list_display = ('base_currency', 'target_currency', 'rate', 'is_active', 'updated_at')
    list_filter = ('base_currency', 'target_currency', 'is_active')

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'user', 'action', 'entity_type', 'entity_id', 'ip_address')
    list_filter = ('action', 'entity_type')
    search_fields = ('user__email', 'entity_id', 'ip_address', 'action')
    readonly_fields = [f.name for f in AuditLog._meta.fields]

@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'subject', 'is_resolved', 'created_at')
    list_filter = ('is_resolved', 'created_at')
    search_fields = ('full_name', 'email', 'subject', 'message')

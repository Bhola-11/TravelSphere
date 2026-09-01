from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import TravelSphereUser, CustomerProfile, AgencyProfile, UserAddress, KYCDocument, UserActivityLog

@admin.register(TravelSphereUser)
class TravelSphereUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_verified', 'kyc_status', 'is_staff', 'date_joined')
    list_filter = ('role', 'is_verified', 'kyc_status', 'is_staff', 'is_active')
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    ordering = ('-date_joined',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone_number', 'avatar')}),
        ('Role & Verification', {'fields': ('role', 'is_verified', 'kyc_status')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'nationality', 'passport_number', 'loyalty_points', 'preferred_currency')
    search_fields = ('user__email', 'passport_number', 'nationality')

@admin.register(AgencyProfile)
class AgencyProfileAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'trade_license_number', 'official_email', 'is_approved', 'commission_percentage')
    list_filter = ('is_approved',)
    search_fields = ('company_name', 'trade_license_number', 'official_email')

@admin.register(KYCDocument)
class KYCDocumentAdmin(admin.ModelAdmin):
    list_display = ('user', 'document_type', 'document_number', 'is_verified', 'created_at')
    list_filter = ('document_type', 'is_verified')
    search_fields = ('user__email', 'document_number')

@admin.register(UserAddress)
class UserAddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'address_title', 'city', 'country', 'is_default')

@admin.register(UserActivityLog)
class UserActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'ip_address', 'created_at')
    list_filter = ('activity_type',)
    search_fields = ('user__email', 'description', 'ip_address')

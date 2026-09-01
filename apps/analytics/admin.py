from django.contrib import admin
from .models import UserSearchLog, PackageViewLog, RevenueDailyMetric, DynamicPriceAdjustmentLog

@admin.register(UserSearchLog)
class UserSearchLogAdmin(admin.ModelAdmin):
    list_display = ('search_query', 'user', 'results_count', 'created_at')
    search_fields = ('search_query', 'user__email')

@admin.register(RevenueDailyMetric)
class RevenueDailyMetricAdmin(admin.ModelAdmin):
    list_display = ('date', 'gross_revenue', 'net_revenue', 'total_bookings_count', 'new_users_registered')

admin.site.register(PackageViewLog)
admin.site.register(DynamicPriceAdjustmentLog)

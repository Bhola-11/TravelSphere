from django.contrib import admin
from .models import TransportOperator, StationStop, TransportRoute, TransportSchedule, SeatClass

class SeatClassInline(admin.TabularInline):
    model = SeatClass
    extra = 2

@admin.register(TransportOperator)
class TransportOperatorAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'transport_type', 'rating')
    list_filter = ('transport_type',)

@admin.register(StationStop)
class StationStopAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'city', 'station_type')
    list_filter = ('station_type', 'city__country')
    search_fields = ('name', 'code', 'city__name')

@admin.register(TransportRoute)
class TransportRouteAdmin(admin.ModelAdmin):
    list_display = ('route_code', 'operator', 'origin_station', 'destination_station', 'estimated_duration_minutes')
    search_fields = ('route_code', 'operator__name')

@admin.register(TransportSchedule)
class TransportScheduleAdmin(admin.ModelAdmin):
    list_display = ('route', 'departure_time', 'arrival_time', 'vehicle_identifier', 'is_direct', 'is_active')
    list_filter = ('route__operator__transport_type', 'is_direct', 'is_active')
    inlines = [SeatClassInline]

@admin.register(SeatClass)
class SeatClassAdmin(admin.ModelAdmin):
    list_display = ('schedule', 'class_type', 'base_price', 'total_capacity', 'booked_count')
    list_filter = ('class_type',)

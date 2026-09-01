from django.contrib import admin
from .models import (
    TourCategory, TourGuide, TourPackage, DayItinerary, ItineraryActivity,
    TourInclusionExclusion, TourDepartureDate, SeasonalSurcharge,
    TourPackingItem, TourFAQ
)

class DayItineraryInline(admin.StackedInline):
    model = DayItinerary
    extra = 1

class TourInclusionExclusionInline(admin.TabularInline):
    model = TourInclusionExclusion
    extra = 2

class TourDepartureDateInline(admin.TabularInline):
    model = TourDepartureDate
    extra = 1

class SeasonalSurchargeInline(admin.TabularInline):
    model = SeasonalSurcharge
    extra = 1

class TourFAQInline(admin.TabularInline):
    model = TourFAQ
    extra = 1

@admin.register(TourPackage)
class TourPackageAdmin(admin.ModelAdmin):
    list_display = ('title', 'code', 'destination', 'category', 'duration_days', 'base_price_adult', 'is_featured', 'booking_count', 'is_active')
    list_filter = ('is_featured', 'is_active', 'difficulty_level', 'category', 'destination')
    search_fields = ('title', 'code', 'destination__title')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [DayItineraryInline, TourInclusionExclusionInline, TourDepartureDateInline, SeasonalSurchargeInline, TourFAQInline]

@admin.register(DayItinerary)
class DayItineraryAdmin(admin.ModelAdmin):
    list_display = ('tour_package', 'day_number', 'title', 'meals_included', 'overnight_city')
    list_filter = ('tour_package',)

@admin.register(ItineraryActivity)
class ItineraryActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'day_itinerary', 'start_time', 'end_time', 'is_optional', 'extra_cost')

@admin.register(TourGuide)
class TourGuideAdmin(admin.ModelAdmin):
    list_display = ('user', 'experience_years', 'languages_spoken', 'rating')

admin.site.register(TourCategory)
admin.site.register(TourDepartureDate)
admin.site.register(SeasonalSurcharge)
admin.site.register(TourPackingItem)
admin.site.register(TourFAQ)

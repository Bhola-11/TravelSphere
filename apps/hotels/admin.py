from django.contrib import admin
from .models import Amenity, HotelChain, HotelProperty, HotelImage, RoomType, RoomInventory, HotelMealPlan

class HotelImageInline(admin.TabularInline):
    model = HotelImage
    extra = 2

class RoomTypeInline(admin.StackedInline):
    model = RoomType
    extra = 1

class HotelMealPlanInline(admin.TabularInline):
    model = HotelMealPlan
    extra = 1

@admin.register(HotelProperty)
class HotelPropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'city', 'star_rating', 'property_type', 'is_featured', 'rating_average', 'is_active')
    list_filter = ('star_rating', 'property_type', 'is_featured', 'city__country')
    search_fields = ('title', 'city__name', 'address')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [HotelImageInline, RoomTypeInline, HotelMealPlanInline]

@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'hotel', 'category', 'base_price_per_night', 'total_rooms_count', 'is_active')
    list_filter = ('category', 'hotel')
    search_fields = ('name', 'hotel__title')

@admin.register(RoomInventory)
class RoomInventoryAdmin(admin.ModelAdmin):
    list_display = ('room_type', 'date', 'available_rooms', 'booked_rooms', 'price_override', 'is_blocked')
    list_filter = ('date', 'is_blocked')

admin.site.register(Amenity)
admin.site.register(HotelChain)
admin.site.register(HotelMealPlan)

from django.contrib import admin
from .models import Review, ReviewImage, ReviewReply

class ReviewImageInline(admin.TabularInline):
    model = ReviewImage
    extra = 1

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'rating', 'tour_package', 'hotel', 'is_verified_booking', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_approved', 'is_verified_booking')
    search_fields = ('title', 'comment', 'user__email')
    inlines = [ReviewImageInline]

admin.site.register(ReviewReply)

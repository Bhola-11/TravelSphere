"""
Reviews Forms: User Review Submission & Moderation Forms.
"""
from django import forms
from .models import Review
from apps.core.constants import ReviewRating

class SubmitReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('rating', 'title', 'comment')
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Summarize your experience (e.g. Unforgettable tour!)'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Share details of your journey, itinerary, accommodation, and guide...'}),
        }

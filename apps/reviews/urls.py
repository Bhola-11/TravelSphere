from django.urls import path
from .views import SubmitTourReviewView, SubmitHotelReviewView

app_name = 'reviews'

urlpatterns = [
    path('tour/<int:pk>/submit/', SubmitTourReviewView.as_view(), name='submit_tour_review'),
    path('hotel/<int:pk>/submit/', SubmitHotelReviewView.as_view(), name='submit_hotel_review'),
]

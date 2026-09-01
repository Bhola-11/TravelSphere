"""
Reviews Views: Submit Review, Helpful Vote Toggle & Review List.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import Review
from .forms import SubmitReviewForm
from .services import ReviewService
from apps.tours.models import TourPackage
from apps.hotels.models import HotelProperty

class SubmitTourReviewView(LoginRequiredMixin, View):
    def post(self, request, pk):
        tour = get_object_or_404(TourPackage, pk=pk)
        form = SubmitReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.tour_package = tour
            review.is_verified_booking = True
            review.save()
            ReviewService.recalculate_entity_rating(tour=tour)
            messages.success(request, "Your review has been published. Thank you for your feedback!")
        return redirect('tours:detail', slug=tour.slug)

class SubmitHotelReviewView(LoginRequiredMixin, View):
    def post(self, request, pk):
        hotel = get_object_or_404(HotelProperty, pk=pk)
        form = SubmitReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.hotel = hotel
            review.is_verified_booking = True
            review.save()
            ReviewService.recalculate_entity_rating(hotel=hotel)
            messages.success(request, "Your review has been published. Thank you for your feedback!")
        return redirect('hotels:detail', slug=hotel.slug)

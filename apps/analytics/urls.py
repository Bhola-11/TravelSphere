from django.urls import path
from .views import AdminAnalyticsDashboardView, RecommendationFeedView

app_name = 'analytics'

urlpatterns = [
    path('dashboard/', AdminAnalyticsDashboardView.as_view(), name='dashboard'),
    path('recommendations/', RecommendationFeedView.as_view(), name='recommendations'),
]

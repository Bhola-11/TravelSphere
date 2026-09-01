from django.urls import path
from .views import TourPackageListView, TourPackageDetailView, TourQuoteAjaxView

app_name = 'tours'

urlpatterns = [
    path('', TourPackageListView.as_view(), name='list'),
    path('quote/<int:pk>/', TourQuoteAjaxView.as_view(), name='quote_ajax'),
    path('<slug:slug>/', TourPackageDetailView.as_view(), name='detail'),
]

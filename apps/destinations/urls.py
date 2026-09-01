from django.urls import path
from .views import (
    DestinationListView, DestinationDetailView, ContinentExplorerView,
    CountryDetailView, POIDetailView
)

app_name = 'destinations'

urlpatterns = [
    path('', DestinationListView.as_view(), name='list'),
    path('continent/<slug:slug>/', ContinentExplorerView.as_view(), name='continent_detail'),
    path('country/<slug:slug>/', CountryDetailView.as_view(), name='country_detail'),
    path('poi/<slug:slug>/', POIDetailView.as_view(), name='poi_detail'),
    path('<slug:slug>/', DestinationDetailView.as_view(), name='detail'),
]

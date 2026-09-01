from django.urls import path
from .views import TransportSearchView, TransportScheduleDetailView

app_name = 'transports'

urlpatterns = [
    path('', TransportSearchView.as_view(), name='search'),
    path('list/', TransportSearchView.as_view(), name='list'),
    path('<int:pk>/', TransportScheduleDetailView.as_view(), name='detail'),
]

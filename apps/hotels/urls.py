from django.urls import path
from .views import HotelListView, HotelDetailView, RoomQuoteAjaxView

app_name = 'hotels'

urlpatterns = [
    path('', HotelListView.as_view(), name='list'),
    path('room-quote/<int:pk>/', RoomQuoteAjaxView.as_view(), name='room_quote_ajax'),
    path('<slug:slug>/', HotelDetailView.as_view(), name='detail'),
]

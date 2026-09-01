from django.urls import path
from .views import PaymentInitiateView, InvoiceDetailView

app_name = 'payments'

urlpatterns = [
    path('initiate/<uuid:order_id>/', PaymentInitiateView.as_view(), name='initiate'),
    path('invoice/<uuid:pk>/', InvoiceDetailView.as_view(), name='invoice_detail'),
]

"""
Payments Views: Checkout Payment Portal, Gateway Callback Handler & Invoice Downloader.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import PaymentTransaction, Invoice, Coupon
from .forms import PaymentSelectionForm, ApplyCouponForm
from .services import PaymentGatewayService
from apps.bookings.models import BookingOrder

class PaymentInitiateView(LoginRequiredMixin, View):
    template_name = 'payments/payment_portal.html'

    def get(self, request, order_id):
        order = get_object_or_404(BookingOrder, id=order_id, customer=request.user)
        form = PaymentSelectionForm()
        coupon_form = ApplyCouponForm()
        return render(request, self.template_name, {
            'order': order,
            'form': form,
            'coupon_form': coupon_form
        })

    def post(self, request, order_id):
        order = get_object_or_404(BookingOrder, id=order_id, customer=request.user)
        form = PaymentSelectionForm(request.POST)
        if form.is_valid():
            method = form.cleaned_data['payment_method']
            txn = PaymentGatewayService.process_payment(order, method, request.user)
            messages.success(request, f"Payment of ${order.total_amount} successful! Confirmation #{order.booking_reference}")
            return redirect('bookings:confirmation', pk=order.id)
        
        return render(request, self.template_name, {'order': order, 'form': form, 'coupon_form': ApplyCouponForm()})

class InvoiceDetailView(LoginRequiredMixin, DetailView):
    model = Invoice
    template_name = 'payments/invoice_detail.html'
    context_object_name = 'invoice'
    pk_url_kwarg = 'pk'

    def get_queryset(self):
        if self.request.user.is_staff:
            return Invoice.objects.all()
        return Invoice.objects.filter(booking__customer=self.request.user)

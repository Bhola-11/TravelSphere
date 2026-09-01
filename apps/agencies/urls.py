from django.urls import path
from .views import AgencyDashboardView, AgencyPackageListView, AgencyPayoutRequestView

app_name = 'agencies'

urlpatterns = [
    path('dashboard/', AgencyDashboardView.as_view(), name='dashboard'),
    path('packages/', AgencyPackageListView.as_view(), name='packages'),
    path('payouts/request/', AgencyPayoutRequestView.as_view(), name='payout_request'),
]

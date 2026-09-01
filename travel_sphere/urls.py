from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from apps.core.views import HomeView, AboutView, ContactView, TermsView, PrivacyView, FAQView, CurrencySwitcherView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('favicon.ico', RedirectView.as_view(url='/static/images/favicon.svg', permanent=True), name='favicon'),
    path('', HomeView.as_view(), name='home'),
    path('about/', AboutView.as_view(), name='about'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('terms/', TermsView.as_view(), name='terms'),
    path('privacy/', PrivacyView.as_view(), name='privacy'),
    path('faq/', FAQView.as_view(), name='faq'),
    path('currency/switch/', CurrencySwitcherView.as_view(), name='switch_currency'),
    
    # App URLs
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('destinations/', include('apps.destinations.urls', namespace='destinations')),
    path('tours/', include('apps.tours.urls', namespace='tours')),
    path('hotels/', include('apps.hotels.urls', namespace='hotels')),
    path('transports/', include('apps.transports.urls', namespace='transports')),
    path('bookings/', include('apps.bookings.urls', namespace='bookings')),
    path('payments/', include('apps.payments.urls', namespace='payments')),
    path('agencies/', include('apps.agencies.urls', namespace='agencies')),
    path('reviews/', include('apps.reviews.urls', namespace='reviews')),
    path('analytics/', include('apps.analytics.urls', namespace='analytics')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

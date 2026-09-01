"""
Template Context Processors for Global Variables.
"""
from apps.core.services import ConfigService
from apps.core.constants import CurrencyCode

def system_settings(request):
    config = ConfigService.get_config()
    return {
        'SITE_CONFIG': config,
        'SITE_NAME': config.site_name,
        'SITE_TAGLINE': config.tagline,
        'SUPPORT_EMAIL': config.contact_email,
        'SUPPORT_PHONE': config.contact_phone,
    }

def currency_context(request):
    current_currency = request.session.get('currency', 'USD')
    return {
        'CURRENT_CURRENCY': current_currency,
        'SUPPORTED_CURRENCIES': [c[0] for c in CurrencyCode.choices],
    }

def cart_summary(request):
    cart = request.session.get('travel_cart', {'items': [], 'total_count': 0, 'subtotal': 0.0})
    return {
        'CART_TOTAL_ITEMS': cart.get('total_count', 0),
        'CART_SUBTOTAL': cart.get('subtotal', 0.0),
    }

def navigation_context(request):
    return {
        'NAV_DESTINATIONS_ACTIVE': request.path.startswith('/destinations/'),
        'NAV_TOURS_ACTIVE': request.path.startswith('/tours/'),
        'NAV_HOTELS_ACTIVE': request.path.startswith('/hotels/'),
        'NAV_TRANSPORTS_ACTIVE': request.path.startswith('/transports/'),
        'NAV_AGENCIES_ACTIVE': request.path.startswith('/agencies/'),
    }

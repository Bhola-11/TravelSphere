"""
Custom Template Tags & Filters for TravelSphere.
"""
from decimal import Decimal
from django import template
from django.utils.safestring import mark_safe
from apps.core.services import CurrencyService

register = template.Library()

@register.filter(name='currency')
def currency_filter(amount, target_currency=None):
    if amount is None or amount == '':
        return '$0.00'
    try:
        dec_amount = Decimal(str(amount))
    except Exception:
        return str(amount)
    
    curr = target_currency or 'USD'
    return CurrencyService.format_price(dec_amount, curr)

@register.filter(name='convert_currency')
def convert_currency_filter(amount, request):
    if not amount:
        return '$0.00'
    target_currency = getattr(request, 'currency', 'USD')
    try:
        dec_amount = Decimal(str(amount))
        converted = CurrencyService.convert_amount(dec_amount, 'USD', target_currency)
        return CurrencyService.format_price(converted, target_currency)
    except Exception:
        return f"${amount}"

@register.simple_tag
def render_stars(rating, max_stars=5):
    try:
        r = float(rating or 0)
    except (ValueError, TypeError):
        r = 0.0
    
    html = '<div class="flex items-center text-amber-400 gap-0.5">'
    full_stars = int(r)
    has_half = (r - full_stars) >= 0.5
    empty_stars = max_stars - full_stars - (1 if has_half else 0)

    for _ in range(full_stars):
        html += '<i class="bi bi-star-fill text-warning"></i>'
    if has_half:
        html += '<i class="bi bi-star-half text-warning"></i>'
    for _ in range(max(0, empty_stars)):
        html += '<i class="bi bi-star text-muted"></i>'
    
    html += f'<span class="ms-1 text-sm font-bold text-dark">{r:.1f}</span></div>'
    return mark_safe(html)

@register.filter(name='status_badge')
def status_badge(status):
    status_classes = {
        'CONFIRMED': 'badge bg-success text-white',
        'COMPLETED': 'badge bg-primary text-white',
        'PENDING_PAYMENT': 'badge bg-warning text-dark',
        'CANCELLED': 'badge bg-danger text-white',
        'REFUNDED': 'badge bg-secondary text-white',
        'IN_PROGRESS': 'badge bg-info text-white',
        'VERIFIED': 'badge bg-success text-white',
        'UNDER_REVIEW': 'badge bg-warning text-dark',
        'REJECTED': 'badge bg-danger text-white',
    }
    css_class = status_classes.get(status, 'badge bg-light text-dark border')
    return mark_safe(f'<span class="{css_class} px-2 py-1 rounded-pill">{status}</span>')

"""
Core Middlewares: Request Timing, Security Headers, Maintenance Check, and User Audit IP Tracker.
"""
import time
from django.http import HttpResponse
from django.template import loader
from apps.core.services import ConfigService

class RequestTimingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        duration = time.time() - start_time
        response['X-Request-Duration-MS'] = f"{duration * 1000:.2f}"
        return response

class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        request.client_ip = ip
        request.client_user_agent = request.META.get('HTTP_USER_AGENT', '')
        return self.get_response(request)

class RoleAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Attach active currency to request
        if hasattr(request, 'session'):
            if 'currency' not in request.session:
                request.session['currency'] = 'USD'
            request.currency = request.session.get('currency', 'USD')
        else:
            request.currency = 'USD'
        
        # Check maintenance mode
        if not request.path.startswith('/admin/'):
            config = ConfigService.get_config()
            if config.maintenance_mode and not (request.user.is_authenticated and request.user.is_staff):
                return HttpResponse("Service Temporarily Unavailable for Maintenance", status=503)

        return self.get_response(request)

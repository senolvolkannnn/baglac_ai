from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
import time

class RequestTimingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.start_time = time.time()
    
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            total_time = time.time() - request.start_time
            response['X-Request-Time'] = str(total_time)
        return response

class SecurityHeadersMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        if settings.DEBUG is False:
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response 
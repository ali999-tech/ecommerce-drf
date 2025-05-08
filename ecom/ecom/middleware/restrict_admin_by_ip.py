from django.http import HttpResponseForbidden

ALLOWED_ADMIN_IPS = []

class RestrictAdminByIPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        if request.path.startswith('/admin/'):
            ip = self.get_client_ip(request)
            if ip not in ALLOWED_ADMIN_IPS:
                return HttpResponseForbidden('<h1> Forbidden </h1> <p> Access denied. </p>')
        return self.get_response(request)
    def get_client_ip(self, request):
        x_forwaded_for = request.META.get('HTTP_X_FORWADED_FOR')
        if x_forwaded_for:
            ip = x_forwaded_for.split(', ')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
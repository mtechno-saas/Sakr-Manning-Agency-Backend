import datetime
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone

class ActiveUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        if request.user.is_authenticated:
            try:
                # Update last seen timestamp in cache
                # Key format: online_user_<user_id>
                # Timeout: 1 minute (60 seconds)
                current_time = timezone.now()
                cache.set(f'online_user_{request.user.id}', current_time, 60)
            except Exception:
                # Fail silently if cache is not available
                pass
                
        return response

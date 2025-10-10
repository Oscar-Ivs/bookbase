# bookbase/middleware.py
from django.conf import settings
from django.shortcuts import redirect

def canonical_www_redirect(get_response):
    def middleware(request):
        if not settings.DEBUG:
            host = request.get_host().split(':')[0].lower()
            if host == "bookbase.net":
                return redirect(
                    f"https://www.bookbase.net{request.get_full_path()}",
                    permanent=True
                )
        return get_response(request)
    return middleware

# middleware.py
from django.shortcuts import redirect

# Redirects root domain to www version
def canonical_www_redirect(get_response):
    def middleware(request):
        host = request.get_host()
        # Redirect only if user visits non-www domain
        if host == "bookbase.net":
            return redirect(f"https://www.bookbase.net{request.get_full_path()}", permanent=True)
        return get_response(request)
    return middleware

# bookbase/urls.py  (project-level)
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import RedirectView

from django.conf import settings
from django.conf.urls.static import static as serve_static  # alias to avoid name clash

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('books.urls')),

    # Serve /favicon.ico by redirecting to the static file
    re_path(r'^favicon\.ico$', RedirectView.as_view(
        url='/static/img/favicon_bookbase.ico', permanent=True
    )),
]

# Serve uploaded media in development
if settings.DEBUG:
    urlpatterns += serve_static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

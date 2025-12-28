"""
URL configuration for dachuang management system project.
"""

from django.contrib import admin
from django.urls import URLPattern, URLResolver, include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns: list[URLPattern | URLResolver] = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/", include("apps.users.urls")),
    path("api/v1/projects/", include("apps.projects.urls")),
    path("api/v1/reviews/", include("apps.reviews.urls")),
    path("api/v1/notifications/", include("apps.notifications.urls")),
    path("api/v1/dictionaries/", include("apps.dictionaries.urls")),
    path("api/v1/system-settings/", include("apps.system_settings.urls")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

"""
TreeGuardian — Root URL Configuration

At Level 1 we wire:
    /api/auth/   →  apps.users.urls
    /api/trees/  →  apps.trees.urls
    /admin/      →  Django admin
    /api/        →  DRF browsable API login (for the browser UI)
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse


@api_view(["GET"])
def api_root(request, format=None):
    """
    Welcome to the TreeGuardian API.
    This root endpoint lists all available top-level routes.
    """
    return Response(
        {
            "message": "🌳 Welcome to TreeGuardian API",
            "version": "1.0",
            "endpoints": {
                "trees": reverse("tree-list", request=request, format=format),
                "register": reverse("register", request=request, format=format),
                "login": reverse("login", request=request, format=format),
                "admin": request.build_absolute_uri("/admin/"),
            },
        }
    )


urlpatterns = [
    # Django Admin
    path("admin/", admin.site.urls),

    # DRF browsable API login/logout (needed for the browser UI)
    path("api-auth/", include("rest_framework.urls")),

    # API root — shows all top-level URLs
    path("api/", api_root, name="api-root"),

    # App routes
    path("api/auth/", include("apps.users.urls")),
    path("api/trees/", include("apps.trees.urls")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

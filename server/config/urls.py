"""
URL configuration for minimalist project management app.
"""
from django.contrib import admin
from django.conf import settings
from django.http import JsonResponse
from django.urls import include, path


def health_check(request):
    """Health check endpoint for Docker."""
    return JsonResponse({'status': 'healthy'})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check),
    path('api/auth/', include('accounts.urls')),
    path('api/v1/', include('projects.api.urls')),
]

# OpenAPI schema (dev only)
if settings.DEBUG:
    from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

    urlpatterns += [
        path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
        path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    ]

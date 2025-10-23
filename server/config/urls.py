"""
URL configuration for minimalist todo app.
"""
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def health_check(request):
    """Health check endpoint for Docker."""
    return JsonResponse({'status': 'healthy'})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check),
    path('api/', include('todos.urls')),
]





"""
URL configuration for Alexaticks project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Página principal (home) se queda en la raíz
    path('', include(('home.urls', 'home'), namespace='home')),
    
    # Movemos cuentas y reclamos a sus propias carpetas virtuales para evitar choques
    path('cuentas/', include('cuentas.urls')),
    path('reclamos/', include('reclamos.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
from django.urls import path
from . import views


urlpatterns = [
    # ==========================================
    # RUTAS DEL CLIENTE
    # ==========================================
    path('', views.dashboard_cliente, name='dashboard_cliente'),
    path('reclamo/crear/', views.crear_reclamo, name='crear_reclamo'),
    path('reclamo/<int:pk>/', views.detalle_reclamo, name='detalle_reclamo'),

    # ==========================================
    # RUTAS DE EMPLEADOS (NUEVAS)
    # ==========================================
    path('calidad/panel/', views.panel_calidad, name='panel_calidad'),
    path('empleado/panel/', views.panel_empleado, name='panel_empleado'),
]
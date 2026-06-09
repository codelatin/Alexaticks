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
    # RUTAS DE EMPLEADOS
    # ==========================================
    path('calidad/panel/', views.panel_calidad, name='panel_calidad'),
    path('empleado/panel/', views.panel_empleado, name='panel_empleado'),
    path('poscosecha/panel/', views.panel_poscosecha, name='panel_poscosecha'),
    path('produccion/panel/', views.panel_produccion, name='panel_produccion'),
    path('exportaciones/panel/', views.panel_exportaciones, name='panel_exportaciones'),

    # ==========================================
    # RUTA DE SUPERADMIN
    # ==========================================
    path('gerencia/', views.panel_gerencia, name='panel_gerencia'),
]
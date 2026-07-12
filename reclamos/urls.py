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
    path('gerencia/exportar/excel/', views.exportar_excel, name='exportar_excel'),
    path('gerencia/exportar/pdf/', views.exportar_pdf, name='exportar_pdf'),
    path('gerencia/crear-usuario/', views.crear_usuario, name='crear_usuario'),  # ← NUEVA
    path('gerencia/usuarios/', views.lista_usuarios, name='lista_usuarios'), 
    path('gerencia/usuario/<int:pk>/editar/', views.editar_usuario, name='editar_usuario'),
    path('gerencia/usuario/<int:pk>/eliminar/', views.eliminar_usuario, name='eliminar_usuario'),
]
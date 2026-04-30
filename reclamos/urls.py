from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_cliente, name='dashboard_cliente'),
    path('reclamo/nuevo/', views.crear_reclamo, name='crear_reclamo'),
    path('reclamo/<int:pk>/', views.detalle_reclamo, name='detalle_reclamo'),
    path('secretaria/panel/', views.panel_secretaria, name='panel_secretaria'),
]
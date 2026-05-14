from django.contrib import admin
from .models import (
    CategoriaProblema, TipoProblema, MotivoRechazo, 
    Reclamo, Evidencia, Respuesta, AsignacionArea, HistorialEstado
)

# ==========================================
# ADMIN DE CATÁLOGOS BÁSICOS (Nuevos)
# ==========================================
@admin.register(CategoriaProblema)
class CategoriaProblemaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'orden')
    ordering = ('orden',)

@admin.register(TipoProblema)
class TipoProblemaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'activo')
    list_filter = ('categoria', 'activo')

@admin.register(MotivoRechazo)
class MotivoRechazoAdmin(admin.ModelAdmin):
    list_display = ('texto', 'activo')

# ==========================================
# ADMIN DE TRAZABILIDAD (Nuevos)
# ==========================================
@admin.register(AsignacionArea)
class AsignacionAreaAdmin(admin.ModelAdmin):
    list_display = ('reclamo', 'responsable', 'departamento', 'fecha_asignacion')
    list_filter = ('departamento',)

@admin.register(HistorialEstado)
class HistorialEstadoAdmin(admin.ModelAdmin):
    list_display = ('reclamo', 'estado_anterior', 'estado_nuevo', 'usuario', 'created_at')
    list_filter = ('estado_nuevo',)
    readonly_fields = ('reclamo', 'estado_anterior', 'estado_nuevo', 'usuario', 'created_at')


# ==========================================
# INLINES PARA EL RECLAMO
# ==========================================
class EvidenciaInline(admin.TabularInline):
    model = Evidencia
    extra = 0
    readonly_fields = ('uploaded_at',)
    fields = ('archivo', 'descripcion_adjunto', 'uploaded_at') # <-- CAMBIO: Agregado campo


class RespuestaInline(admin.TabularInline):
    model = Respuesta
    extra = 0
    readonly_fields = ('created_at',)
    fields = ('autor', 'mensaje', 'es_interno', 'created_at') # <-- CAMBIO: Agregado campo


# ==========================================
# ADMIN PRINCIPAL DEL RECLAMO
# ==========================================
@admin.register(Reclamo)
class ReclamoAdmin(admin.ModelAdmin):
    # <-- CAMBIO: Quitado 'numero_cargamento', agregados 'numero_guia_master', 'inspector_calidad'
    list_display = ('numero', 'cliente', 'numero_guia_master', 'tipo_problema', 'estado', 'inspector_calidad', 'created_at')
    
    # <-- CAMBIO: Ahora se puede filtrar por la categoría del problema usando '__' (double underscore lookup)
    list_filter = ('estado', 'tipo_problema__categoria', 'created_at')
    
    search_fields = ('numero', 'numero_guia_master', 'cliente__user__first_name', 'cliente__company_name')
    inlines = [EvidenciaInline, RespuestaInline]
    
    # <-- CAMBIO: Agregados los nuevos campos de solo lectura y el inspector
    readonly_fields = ('numero', 'created_at', 'updated_at')
    
    # Opcional: Organizar cómo se ve el formulario al editar un reclamo
    fieldsets = (
        (None, {
            'fields': ('numero', 'cliente', 'estado', 'tipo_problema', 'variedad_rosa')
        }),
        ('Información de Envío', {
            'fields': ('numero_guia_master', 'fecha_despacho', 'zona_horaria_cliente')
        }),
        ('Detalle del Problema', {
            'fields': ('descripcion',)
        }),
        ('Gestión de Calidad', {
            'fields': ('inspector_calidad', 'motivo_rechazo', 'observaciones_internas_calidad'),
            'classes': ('collapse',) # Se muestra colapsado para no saturar la vista
        }),
    )
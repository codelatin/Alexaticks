from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Reclamo, Evidencia, Respuesta


class EvidenciaInline(admin.TabularInline):
    model = Evidencia
    extra = 0
    readonly_fields = ('uploaded_at',)


class RespuestaInline(admin.TabularInline):
    model = Respuesta
    extra = 0
    readonly_fields = ('created_at',)
    fields = ('autor', 'mensaje', 'created_at')


@admin.register(Reclamo)
class ReclamoAdmin(admin.ModelAdmin):
    list_display = ('numero', 'cliente', 'numero_cargamento', 'tipo_problema', 'estado', 'created_at')
    list_filter = ('estado', 'tipo_problema', 'created_at')
    search_fields = ('numero', 'numero_cargamento', 'cliente__user__first_name', 'cliente__company_name')
    inlines = [EvidenciaInline, RespuestaInline]
    readonly_fields = ('numero', 'created_at', 'updated_at')
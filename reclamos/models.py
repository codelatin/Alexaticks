import os
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from cuentas.models import Perfil

def evidencia_path(instance, filename):
    return f'reclamos/{instance.reclamo.numero}/{filename}'

# ==========================================
# CATÁLOGOS (RF-006 y RF-022)
# ==========================================
class CategoriaProblema(models.Model):
    """Ej: Empaque, Contenido, Calidad de Producto"""
    nombre = models.CharField(max_length=100, verbose_name=_('Categoría'))
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _('Categoría de Problema')
        verbose_name_plural = _('Categorías de Problemas')
        ordering = ['orden']

    def __str__(self):
        return self.nombre

class TipoProblema(models.Model):
    """Ej: Mal empaque, Botrytis, Faltante de flor"""
    categoria = models.ForeignKey(CategoriaProblema, on_delete=models.CASCADE, related_name='tipos')
    nombre = models.CharField(max_length=150, verbose_name=_('Tipo de Problema'))
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Tipo de Problema')
        verbose_name_plural = _('Tipos de Problemas')

    def __str__(self):
        return f"{self.categoria.nombre} > {self.nombre}"

class MotivoRechazo(models.Model):
    """Catálogo para que Calidad seleccione al rechazar (RF-010)"""
    texto = models.CharField(max_length=200, verbose_name=_('Motivo de rechazo'))
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Motivo de Rechazo')

    def __str__(self):
        return self.texto


# ==========================================
# MODELO PRINCIPAL: RECLAMO
# ==========================================
class Reclamo(models.Model):
    # RF-008: Nuevo formato de número
    def generar_numero(self):
        year = timezone.now().year
        count = Reclamo.objects.filter(created_at__year=year).count() + 1
        # Formato AFF[AÑO]-[CONSECUTIVO]-[PAÍS] (Ej: AFF2025-0001-US)
        pais_code = self.cliente.country[:2].upper() if self.cliente.country else 'XX'
        return f"AFF{year}-{count:04d}-{pais_code}"

    # RF-015: Estados exactos que pide el documento
    ESTADOS = (
        ('pendiente_validacion', _('Pendiente Validación')),
        ('en_validacion', _('En Validación')),
        ('aprobado_pendiente', _('Aprobado - Pendiente Asignación')),
        ('rechazado', _('Rechazado')),
        ('en_proceso', _('En Proceso')),
        ('en_investigacion', _('En Investigación')),
        ('resolucion_propuesta', _('Resolución Propuesta')),
        ('resuelto', _('Resuelto')),
        ('cerrado', _('Cerrado')),
    )

    numero = models.CharField(max_length=25, unique=True, editable=False, verbose_name=_('Número'))
    cliente = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='reclamos', verbose_name=_('Cliente'))
    
    # RF-006: Cambio de choices simples a relación con catálogo
    tipo_problema = models.ForeignKey(TipoProblema, on_delete=models.PROTECT, verbose_name=_('Tipo de problema'))
    variedad_rosa = models.CharField(max_length=100, verbose_name=_('Variedad de rosa'))
    numero_guia_master = models.CharField(max_length=100, verbose_name=_('Número de Guía Master'))
    fecha_despacho = models.DateField(verbose_name=_('Fecha de despacho'))
    
    # RF-006: Mínimo 50 caracteres, máximo 1000 (Se validará en el Form, aquí ponemos TextField)
    descripcion = models.TextField(verbose_name=_('Descripción detallada'))
    
    estado = models.CharField(max_length=25, choices=ESTADOS, default='pendiente_validacion', verbose_name=_('Estado'))
    
    # RF-010: Campos para el proceso de Calidad
    inspector_calidad = models.ForeignKey(
        Perfil, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='reclamos_inspeccionados', verbose_name=_('Inspector de Calidad')
    )
    motivo_rechazo = models.ForeignKey(
        MotivoRechazo, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name=_('Motivo de Rechazo')
    )
    observaciones_internas_calidad = models.TextField(blank=True, verbose_name=_('Observaciones Internas (Calidad)'))
    
    # RF-005 / 3.1: Formato regional de fecha y zona horaria del cliente
    zona_horaria_cliente = models.CharField(max_length=50, default='America/New_York', verbose_name=_('Zona horaria cliente'))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Reclamo')
        verbose_name_plural = _('Reclamos')
        ordering = ['-created_at']
        permissions = [
            ("puede_validar_calidad", "Puede validar reclamos como Control de Calidad"),
            ("puede_ver_gerencia", "Puede ver dashboard gerencial"),
        ]

    def __str__(self):
        return f"{self.numero} — {self.cliente}"

    def save(self, *args, **kwargs):
        if not self.numero:
            self.numero = self.generar_numero()
        super().save(*args, **kwargs)


# ==========================================
# RF-012: DISTRIBUCIÓN MÚLTIPLE
# ==========================================
class AsignacionArea(models.Model):
    """Tabla intermedia porque un reclamo va a VARIOS departamentos/personas al mismo tiempo."""
    reclamo = models.ForeignKey(Reclamo, on_delete=models.CASCADE, related_name='areas_asignadas')
    responsable = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='tareas_reclamos')
    departamento = models.CharField(max_length=100, verbose_name=_('Departamento (ej. Poscosecha)'))
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    accion_tomada = models.TextField(blank=True, verbose_name=_('Acciones tomadas'))
    
    class Meta:
        verbose_name = _('Asignación a Área')
        unique_together = ('reclamo', 'responsable')


# ==========================================
# RF-016: HISTORIAL DE AUDITORÍA (TRAZABILIDAD)
# ==========================================
class HistorialEstado(models.Model):
    """Para saber quién pasó el reclamo de 'En Proceso' a 'Resuelto' y a qué hora exacta."""
    reclamo = models.ForeignKey(Reclamo, on_delete=models.CASCADE, related_name='historial')
    estado_anterior = models.CharField(max_length=25, blank=True)
    estado_nuevo = models.CharField(max_length=25)
    usuario = models.ForeignKey(Perfil, on_delete=models.SET_NULL, null=True)
    comentarios = models.TextField(blank=True, verbose_name=_('Comentarios del cambio'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Historial de Estado')
        ordering = ['created_at']


# ==========================================
# EVIDENCIAS (Mejorado RF-007)
# ==========================================
class Evidencia(models.Model):
    reclamo = models.ForeignKey(Reclamo, on_delete=models.CASCADE, related_name='evidencias')
    archivo = models.FileField(upload_to=evidencia_path, verbose_name=_('Archivo'))
    descripcion_adjunto = models.CharField(max_length=200, blank=True, verbose_name=_('¿Qué muestra esta evidencia?'))
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Evidencia')

    def filename(self):
        return os.path.basename(self.archivo.name)


# ==========================================
# COMUNICACIÓN / RESPUESTAS
# ==========================================
class Respuesta(models.Model):
    reclamo = models.ForeignKey(Reclamo, on_delete=models.CASCADE, related_name='respuestas')
    autor = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='respuestas')
    mensaje = models.TextField(verbose_name=_('Mensaje'))
    es_interno = models.BooleanField(default=False, verbose_name=_('Nota interna (No visible para cliente)'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Respuesta')
        ordering = ['created_at']


# ==========================================
# ENCUESTA DE SATISFACCIÓN (Paso 7 del flujo)
# ==========================================
class EncuestaSatisfaccion(models.Model):
    reclamo = models.OneToOneField(Reclamo, on_delete=models.CASCADE)
    puntuacion = models.PositiveSmallIntegerField(verbose_name=_('Puntuación (1 a 5)'))
    comentarios_finales = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Encuesta de Satisfacción')
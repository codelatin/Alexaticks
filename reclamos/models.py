from django.db import models

# Create your models here.
import os
from django.db import models
from django.utils import timezone
from cuentas.models import Perfil


def evidencia_path(instance, filename):
    """Ruta de almacenamiento: reclamos/RC-2025-0001/evidencia1.jpg"""
    return f'reclamos/{instance.reclamo.numero}/{filename}'


class Reclamo(models.Model):
    TIPOS_PROBLEMA = (
        ('botones_danados', 'Botones dañados'),
        ('rosas_marchitas', 'Rosas marchitas'),
        ('problema_frio', 'Problema de frío'),
        ('variedad_incorrecta', 'Variedad incorrecta'),
        ('cantidad_faltante', 'Cantidad faltante'),
        ('empaque_danado', 'Empaque dañado'),
        ('otro', 'Otro'),
    )

    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En proceso'),
        ('resuelto', 'Resuelto'),
        ('cerrado', 'Cerrado'),
    )

    numero = models.CharField(max_length=20, unique=True, editable=False, verbose_name='Número')
    cliente = models.ForeignKey(
        Perfil, on_delete=models.CASCADE,
        related_name='reclamos',
        verbose_name='Cliente'
    )
    secretaria = models.ForeignKey(
        Perfil, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='reclamos_asignados',
        verbose_name='Secretaria asignada'
    )
    numero_cargamento = models.CharField(max_length=100, verbose_name='Número de cargamento')
    fecha_reclamo = models.DateField(default=timezone.now, verbose_name='Fecha del reclamo')
    variedad_rosa = models.CharField(max_length=100, verbose_name='Variedad de rosa')
    cantidad_afectada = models.PositiveIntegerField(verbose_name='Cantidad afectada')
    tipo_problema = models.CharField(max_length=25, choices=TIPOS_PROBLEMA, verbose_name='Tipo de problema')
    descripcion = models.TextField(verbose_name='Descripción detallada')
    estado = models.CharField(max_length=15, choices=ESTADOS, default='pendiente', verbose_name='Estado')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Creado el')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Actualizado el')

    class Meta:
        verbose_name = 'Reclamo'
        verbose_name_plural = 'Reclamos'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.numero} — {self.cliente}"

    def save(self, *args, **kwargs):
        if not self.numero:
            self.numero = self.generar_numero()
        if not self.secretaria and self.cliente:
            # Asignar automáticamente la secretaria activa del cliente
            asignacion = self.cliente.secretarias_asignadas.filter(is_active=True).first()
            if asignacion:
                self.secretaria = asignacion.secretaria
        super().save(*args, **kwargs)

    def generar_numero(self):
        year = timezone.now().year
        count = Reclamo.objects.filter(created_at__year=year).count() + 1
        return f"RC-{year}-{count:04d}"


class Evidencia(models.Model):
    reclamo = models.ForeignKey(
        Reclamo, on_delete=models.CASCADE,
        related_name='evidencias',
        verbose_name='Reclamo'
    )
    archivo = models.FileField(upload_to=evidencia_path, verbose_name='Archivo')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='Subido el')

    class Meta:
        verbose_name = 'Evidencia'
        verbose_name_plural = 'Evidencias'

    def filename(self):
        return os.path.basename(self.archivo.name)


class Respuesta(models.Model):
    reclamo = models.ForeignKey(
        Reclamo, on_delete=models.CASCADE,
        related_name='respuestas',
        verbose_name='Reclamo'
    )
    autor = models.ForeignKey(
        Perfil, on_delete=models.CASCADE,
        related_name='respuestas',
        verbose_name='Autor'
    )
    mensaje = models.TextField(verbose_name='Mensaje')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Creado el')

    class Meta:
        verbose_name = 'Respuesta'
        verbose_name_plural = 'Respuestas'
        ordering = ['created_at']

    def __str__(self):
        return f"Respuesta de {self.autor} en {self.reclamo.numero}"
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class Perfil(models.Model):
    ROLES = (
        ('cliente_comprador', _('Cliente Comprador')),
        ('empleado', _('Empleado Interno')), 
    )

    DEPARTAMENTOS = (
        ('ventas', _('Ventas')),
        ('calidad', _('Control de Calidad')),
        ('poscosecha', _('Poscosecha')),
        ('produccion', _('Producción')),
        ('exportaciones', _('Exportaciones')),
        ('gerencia', _('Gerencia General')),
        ('admin', _('Administrador TI')),
    )
    
    # <-- CORRECCIÓN 1: Restauramos la tupla IDIOMAS
    IDIOMAS = (
        ('es', _('Español')),
        ('en', _('English')),
        ('ru', _('Русский')),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    
    # <-- CORRECCIÓN 2: Eliminado el campo 'role' duplicado
    role = models.CharField(max_length=20, choices=ROLES, verbose_name=_('Rol'))
    departamento = models.CharField(max_length=20, choices=DEPARTAMENTOS, null=True, blank=True, verbose_name=_('Departamento'))
    
    phone = models.CharField(max_length=30, blank=True, verbose_name=_('Teléfono'))
    company_name = models.CharField(max_length=200, blank=True, verbose_name=_('Empresa'))
    country = models.CharField(max_length=100, blank=True, verbose_name=_('País'))
    preferred_language = models.CharField(
        max_length=2, choices=IDIOMAS, default='es', verbose_name=_('Idioma preferido')
    )
    must_change_password = models.BooleanField(
        default=False, verbose_name=_('Debe cambiar contraseña')
    )
    temp_password_expires_at = models.DateTimeField(
        null=True, blank=True, verbose_name=_('Expiración de contraseña temporal')
    )
    failed_attempts = models.IntegerField(default=0, verbose_name=_('Intentos fallidos'))
    locked_until = models.DateTimeField(
        null=True, blank=True, verbose_name=_('Bloqueado hasta')
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Creado el'))

    class Meta:
        verbose_name = _('Perfil')
        verbose_name_plural = _('Perfiles')

    def __str__(self):
        # Pequeño ajuste para que en el panel de admin se vea más claro quién es quién
        dept = self.get_departamento_display() if self.departamento else ''
        return f"{self.user.get_full_name()} — {dept}".strip(" —")

    @property
    def is_locked(self):
        if self.locked_until and self.locked_until > timezone.now():
            return True
        return False

    @property
    def is_temp_password_expired(self):
        if self.temp_password_expires_at and timezone.now() > self.temp_password_expires_at:
            return True
        return False


# <-- CORRECCIÓN 3: Cambiamos el modelo a "AsignacionVendedor" 
# (Según RF-012 del documento, TODO reclamo debe ir al vendedor asignado al cliente)
class AsignacionVendedor(models.Model):
    vendedor = models.ForeignKey(
        Perfil, on_delete=models.CASCADE,
        # Ahora busca que sea un empleado que pertenezca al departamento de ventas
        limit_choices_to={'role': 'empleado', 'departamento': 'ventas'},
        related_name='clientes_asignados',
        verbose_name=_('Vendedor')
    )
    cliente = models.ForeignKey(
        Perfil, on_delete=models.CASCADE,
        limit_choices_to={'role': 'cliente_comprador'},
        related_name='vendedores_asignados',
        verbose_name=_('Cliente comprador')
    )
    is_active = models.BooleanField(default=True, verbose_name=_('Activa'))
    assigned_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Asignada el'))

    class Meta:
        verbose_name = _('Asignación Vendedor-Cliente')
        verbose_name_plural = _('Asignaciones Vendedor-Cliente')
        unique_together = ('vendedor', 'cliente')

    def __str__(self):
        return f"{self.vendedor} → {self.cliente}"

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Perfil(models.Model):
    ROLES = (
        ('vendedor', 'Vendedor'),
        ('secretaria', 'Secretaria'),
        ('cliente_comprador', 'Cliente Comprador'),
    )

    IDIOMAS = (
        ('es', 'Español'),
        ('en', 'English'),
        ('ru', 'Русский'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    role = models.CharField(max_length=20, choices=ROLES, verbose_name='Rol')
    phone = models.CharField(max_length=30, blank=True, verbose_name='Teléfono')
    company_name = models.CharField(max_length=200, blank=True, verbose_name='Empresa')
    country = models.CharField(max_length=100, blank=True, verbose_name='País')
    preferred_language = models.CharField(
        max_length=2, choices=IDIOMAS, default='es', verbose_name='Idioma preferido'
    )
    must_change_password = models.BooleanField(
        default=False, verbose_name='Debe cambiar contraseña'
    )
    temp_password_expires_at = models.DateTimeField(
        null=True, blank=True, verbose_name='Expiración de contraseña temporal'
    )
    failed_attempts = models.IntegerField(default=0, verbose_name='Intentos fallidos')
    locked_until = models.DateTimeField(
        null=True, blank=True, verbose_name='Bloqueado hasta'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Creado el')

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfiles'

    def __str__(self):
        return f"{self.user.get_full_name()} — {self.get_role_display()}"

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


class AsignacionSecretaria(models.Model):
    secretaria = models.ForeignKey(
        Perfil, on_delete=models.CASCADE,
        limit_choices_to={'role': 'secretaria'},
        related_name='clientes_asignados',
        verbose_name='Secretaria'
    )
    cliente = models.ForeignKey(
        Perfil, on_delete=models.CASCADE,
        limit_choices_to={'role': 'cliente_comprador'},
        related_name='secretarias_asignadas',
        verbose_name='Cliente comprador'
    )
    is_active = models.BooleanField(default=True, verbose_name='Activa')
    assigned_at = models.DateTimeField(auto_now_add=True, verbose_name='Asignada el')

    class Meta:
        verbose_name = 'Asignación Secretaria-Cliente'
        verbose_name_plural = 'Asignaciones Secretaria-Cliente'
        unique_together = ('secretaria', 'cliente')

    def __str__(self):
        return f"{self.secretaria} → {self.cliente}"
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User


@receiver(post_save, sender=User)
def crear_perfil_automatico(sender, instance, created, **kwargs):
    if created:
        from .models import Perfil
        if not hasattr(instance, 'perfil'):
            # Superusuarios y staff → empleado gerencia
            if instance.is_superuser or instance.is_staff:
                Perfil.objects.create(
                    user=instance,
                    role='empleado',
                    departamento='gerencia',
                    preferred_language='es'
                )
            else:
                # Usuarios normales → cliente comprador
                Perfil.objects.create(
                    user=instance,
                    role='cliente_comprador',
                    preferred_language='es'
                )
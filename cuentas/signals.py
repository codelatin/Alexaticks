from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User


@receiver(post_save, sender=User)
def crear_perfil_vendedor_auto(sender, instance, created, **kwargs):
    """
    Cuando se crea un superusuario o staff desde el admin,
    automáticamente se le crea un perfil de vendedor.
    Los clientes se crean desde la vista registrar_cliente_view.
    """
    if created and (instance.is_superuser or instance.is_staff):
        from .models import Perfil
        if not hasattr(instance, 'perfil'):
            Perfil.objects.create(
                user=instance,
                role='vendedor'
            )
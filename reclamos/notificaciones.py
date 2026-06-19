from django.core.mail import send_mail
from django.conf import settings


def enviar_email(destinatario, asunto, mensaje):
    """Función base para enviar emails."""
    try:
        print(f'Enviando email a {destinatario}...')  # ← TEMPORAL
        send_mail(
            subject=asunto,
            message=mensaje,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[destinatario],
            fail_silently=False,
        )
        print(f'Email enviado correctamente a {destinatario}')  # ← TEMPORAL
    except Exception as e:
        print(f'Error enviando email a {destinatario}: {e}')


# ==========================================
# 1. CLIENTE CREA UN RECLAMO
# ==========================================
def notificar_reclamo_creado(reclamo):
    # Al cliente
    enviar_email(
        destinatario=reclamo.cliente.user.email,
        asunto=f'Alexandra Farms — Reclamo {reclamo.numero} recibido',
        mensaje=f"""
Estimado/a {reclamo.cliente.user.get_full_name()},

Su reclamo ha sido registrado exitosamente en nuestro sistema.

Número de caso: {reclamo.numero}
Guía Master: {reclamo.numero_guia_master}
Tipo de problema: {reclamo.tipo_problema}
Estado actual: Pendiente de validación

Nuestro equipo de Control de Calidad revisará su caso a la brevedad.

Atentamente,
Alexandra Farms — Equipo de Calidad
        """.strip()
    )

    # A calidad (notificar que hay un reclamo nuevo)
    from cuentas.models import Perfil
    empleados_calidad = Perfil.objects.filter(
        role='empleado',
        departamento='calidad',
        user__is_active=True
    )
    for emp in empleados_calidad:
        enviar_email(
            destinatario=emp.user.email,
            asunto=f'Nuevo reclamo pendiente — {reclamo.numero}',
            mensaje=f"""
Hola {emp.user.get_full_name()},

Se ha registrado un nuevo reclamo que requiere validación.

Número de caso: {reclamo.numero}
Cliente: {reclamo.cliente.user.get_full_name()}
Empresa: {reclamo.cliente.company_name}
País: {reclamo.cliente.country}
Tipo de problema: {reclamo.tipo_problema}
Guía Master: {reclamo.numero_guia_master}

Por favor ingrese al sistema para revisarlo.

Atentamente,
Alexandra Farms — Sistema de Reclamos
            """.strip()
        )


# ==========================================
# 2. CALIDAD APRUEBA EL RECLAMO
# ==========================================
def notificar_reclamo_aprobado(reclamo, empleado_asignado):
    # Al cliente
    enviar_email(
        destinatario=reclamo.cliente.user.email,
        asunto=f'Alexandra Farms — Reclamo {reclamo.numero} aprobado',
        mensaje=f"""
Estimado/a {reclamo.cliente.user.get_full_name()},

Su reclamo ha sido revisado y aprobado por nuestro departamento de Control de Calidad.

Número de caso: {reclamo.numero}
Estado actual: En proceso
Departamento asignado: {empleado_asignado.get_departamento_display()}

Nuestro equipo trabajará en la resolución de su caso.

Atentamente,
Alexandra Farms — Equipo de Calidad
        """.strip()
    )

    # Al empleado asignado
    enviar_email(
        destinatario=empleado_asignado.user.email,
        asunto=f'Reclamo asignado — {reclamo.numero}',
        mensaje=f"""
Hola {empleado_asignado.user.get_full_name()},

Se le ha asignado un reclamo para su atención.

Número de caso: {reclamo.numero}
Cliente: {reclamo.cliente.user.get_full_name()}
Empresa: {reclamo.cliente.company_name}
País: {reclamo.cliente.country}
Tipo de problema: {reclamo.tipo_problema}
Guía Master: {reclamo.numero_guia_master}

Por favor ingrese al sistema para gestionarlo.

Atentamente,
Alexandra Farms — Sistema de Reclamos
        """.strip()
    )


# ==========================================
# 3. CALIDAD RECHAZA EL RECLAMO
# ==========================================
def notificar_reclamo_rechazado(reclamo):
    motivo = reclamo.motivo_rechazo.texto if reclamo.motivo_rechazo else 'No especificado'
    observaciones = reclamo.observaciones_internas_calidad or 'Sin observaciones adicionales'

    enviar_email(
        destinatario=reclamo.cliente.user.email,
        asunto=f'Alexandra Farms — Reclamo {reclamo.numero} rechazado',
        mensaje=f"""
Estimado/a {reclamo.cliente.user.get_full_name()},

Lamentamos informarle que su reclamo ha sido revisado y no pudo ser aprobado.

Número de caso: {reclamo.numero}
Motivo de rechazo: {motivo}
Observaciones: {observaciones}

Si considera que existe un error, puede contactarnos directamente.

Atentamente,
Alexandra Farms — Equipo de Calidad
        """.strip()
    )


# ==========================================
# 4. NUEVA RESPUESTA EN EL RECLAMO
# ==========================================
def notificar_nueva_respuesta(reclamo, respuesta):
    # Notificar al cliente que hay una respuesta nueva
    enviar_email(
        destinatario=reclamo.cliente.user.email,
        asunto=f'Alexandra Farms — Nueva respuesta en reclamo {reclamo.numero}',
        mensaje=f"""
Estimado/a {reclamo.cliente.user.get_full_name()},

Ha recibido una nueva respuesta en su reclamo.

Número de caso: {reclamo.numero}
Respondido por: {respuesta.autor.user.get_full_name()} ({respuesta.autor.get_departamento_display()})
Mensaje: {respuesta.mensaje}

Ingrese al sistema para ver el detalle completo.

Atentamente,
Alexandra Farms — Equipo de Calidad
        """.strip()
    )

def notificar_reclamo_resuelto(reclamo):
    enviar_email(
        destinatario=reclamo.cliente.user.email,
        asunto=f'Alexandra Farms — Reclamo {reclamo.numero} resuelto',
        mensaje=f"""
Estimado/a {reclamo.cliente.user.get_full_name()},

Nos complace informarle que su reclamo ha sido atendido y resuelto.

Número de caso: {reclamo.numero}
Tipo de problema: {reclamo.tipo_problema}
Estado actual: Resuelto

Por favor ingrese al sistema y confirme si está satisfecho
con la solución para cerrar el caso definitivamente.

Atentamente,
Alexandra Farms — Equipo de Calidad
        """.strip()
    )
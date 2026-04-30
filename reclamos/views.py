from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q          # ← Q importado aquí
from cuentas.models import Perfil
from cuentas.views import role_required
from .models import Reclamo, Evidencia, Respuesta
from .forms import ReclamoForm, RespuestaForm


# =============================================
# DASHBOARD DEL CLIENTE
# =============================================
@role_required('cliente_comprador')
def dashboard_cliente(request):
    perfil = request.user.perfil
    reclamos = Reclamo.objects.filter(cliente=perfil).order_by('-created_at')

    pendientes = reclamos.filter(estado='pendiente').count()
    en_proceso = reclamos.filter(estado='en_proceso').count()
    resueltos = reclamos.filter(estado__in=['resuelto', 'cerrado']).count()

    return render(request, 'reclamos/dashboard_cliente.html', {
        'perfil': perfil,
        'reclamos': reclamos,
        'pendientes': pendientes,
        'en_proceso': en_proceso,
        'resueltos': resueltos,
    })


# =============================================
# CREAR RECLAMO
# =============================================
@role_required('cliente_comprador')
def crear_reclamo(request):
    perfil = request.user.perfil

    if request.method == 'POST':
        form = ReclamoForm(request.POST, request.FILES)
        if form.is_valid():
            reclamo = form.save(commit=False)
            reclamo.cliente = perfil
            reclamo.save()

            archivos = form.cleaned_data.get('archivos')
            if archivos:
                for archivo in archivos:
                    Evidencia.objects.create(reclamo=reclamo, archivo=archivo)

            messages.success(request, 'reclamo_creado')
            return redirect('detalle_reclamo', pk=reclamo.pk)
    else:
        form = ReclamoForm()

    return render(request, 'reclamos/crear_reclamo.html', {
        'form': form,
        'perfil': perfil,
    })


# =============================================
# DETALLE DEL RECLAMO (Cliente y Secretaria)
# =============================================
@role_required('cliente_comprador', 'secretaria')
def detalle_reclamo(request, pk):
    perfil = request.user.perfil
    reclamo = get_object_or_404(Reclamo, pk=pk)

    if perfil.role == 'cliente_comprador' and reclamo.cliente != perfil:
        messages.error(request, 'sin_permiso')
        return redirect('dashboard_cliente')

    if perfil.role == 'secretaria':
        asignaciones = perfil.clientes_asignados.filter(
            cliente=reclamo.cliente, is_active=True
        )
        if not asignaciones.exists():
            messages.error(request, 'sin_permiso')
            return redirect('panel_secretaria')

    respuestas = reclamo.respuestas.select_related('autor__user').all()
    evidencias = reclamo.evidencias.all()

    form = None
    if perfil.role == 'secretaria':
        # Cambiar estado del reclamo
        if 'cambiar_estado' in request.POST:
            nuevo_estado = request.POST.get('nuevo_estado')
            if nuevo_estado in dict(Reclamo.ESTADOS):
                reclamo.estado = nuevo_estado
                reclamo.save(update_fields=['estado'])
                messages.success(request, 'estado_actualizado')
                return redirect('detalle_reclamo', pk=reclamo.pk)

        # Enviar respuesta
        if request.method == 'POST':
            form = RespuestaForm(request.POST)
            if form.is_valid():
                respuesta = form.save(commit=False)
                respuesta.reclamo = reclamo
                respuesta.autor = perfil
                respuesta.save()

                if reclamo.estado == 'pendiente':
                    reclamo.estado = 'en_proceso'
                    reclamo.save(update_fields=['estado'])

                messages.success(request, 'respuesta_enviada')
                return redirect('detalle_reclamo', pk=reclamo.pk)
        else:
            form = RespuestaForm()

    return render(request, 'reclamos/detalle_reclamo.html', {
        'reclamo': reclamo,
        'respuestas': respuestas,
        'evidencias': evidencias,
        'form': form,
        'perfil': perfil,
    })

# =============================================
# PANEL DE LA SECRETARIA
# =============================================
@role_required('secretaria')
def panel_secretaria(request):
    perfil = request.user.perfil

    clientes_ids = perfil.clientes_asignados.filter(
        is_active=True
    ).values_list('cliente_id', flat=True)

    reclamos = Reclamo.objects.filter(
        cliente_id__in=clientes_ids
    ).select_related('cliente__user').order_by('-created_at')

    pendientes = reclamos.filter(estado='pendiente').count()
    en_proceso = reclamos.filter(estado='en_proceso').count()

    clientes_con_reclamos = Perfil.objects.filter(
        id__in=clientes_ids,
        role='cliente_comprador'
    ).annotate(
        reclamos_pendientes=Count(
            'reclamos',
            filter=Q(reclamos__estado='pendiente')   # ← Ahora Q está importado
        )
    ).select_related('user')

    return render(request, 'reclamos/panel_secretaria.html', {
        'perfil': perfil,
        'reclamos': reclamos,
        'pendientes': pendientes,
        'en_proceso': en_proceso,
        'clientes': clientes_con_reclamos,
    })
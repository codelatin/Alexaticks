from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from cuentas.models import Perfil, AsignacionVendedor
from cuentas.views import role_required
from .models import (
    Reclamo, Evidencia, Respuesta, 
    CategoriaProblema, TipoProblema, MotivoRechazo,
    AsignacionArea, HistorialEstado
)
from .forms import ReclamoForm, RespuestaForm


# =============================================
# DASHBOARD DEL CLIENTE
# =============================================
@role_required('cliente_comprador')
def dashboard_cliente(request):
    perfil = request.user.perfil
    reclamos = Reclamo.objects.filter(cliente=perfil).order_by('-created_at')

    # Actualizados los estados según el documento
    pendientes = reclamos.filter(estado__in=['pendiente_validacion', 'en_validacion', 'aprobado_pendiente']).count()
    en_proceso = reclamos.filter(estado__in=['en_proceso', 'en_investigacion', 'resolucion_propuesta']).count()
    finalizados = reclamos.filter(estado__in=['resuelto', 'cerrado', 'rechazado']).count()

    return render(request, 'reclamos/dashboard_cliente.html', {
        'perfil': perfil,
        'reclamos': reclamos,
        'pendientes': pendientes,
        'en_proceso': en_proceso,
        'finalizados': finalizados,
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
            reclamo.save() # El estado 'pendiente_validacion' se asigna por defecto en el modelo

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
# DETALLE DEL RECLAMO (Cliente, Empleados)
# =============================================
@role_required('cliente_comprador', 'empleado')
def detalle_reclamo(request, pk):
    perfil = request.user.perfil
    reclamo = get_object_or_404(Reclamo, pk=pk)

    # Permiso: Solo el cliente dueño puede verlo
    if perfil.role == 'cliente_comprador' and reclamo.cliente != perfil:
        messages.error(request, 'sin_permiso')
        return redirect('dashboard_cliente')

    # Permiso: Empleados solo ven si están asignados al área (o son gerencia/calidad)
    if perfil.role == 'empleado' and perfil.departamento not in ['calidad', 'gerencia']:
        if not AsignacionArea.objects.filter(reclamo=reclamo, responsable=perfil).exists():
            messages.error(request, 'sin_permiso')
            return redirect('panel_empleado')

    respuestas = reclamo.respuestas.select_related('autor__user').all()
    evidencias = reclamo.evidencias.all()

    form = None

    # ==========================================
    # LÓGICA PARA EL DEPARTAMENTO DE CALIDAD
    # ==========================================
    if perfil.departamento == 'calidad':
        if request.method == 'POST' and 'aprobar_reclamo' in request.POST:
            estado_anterior = reclamo.estado
            reclamo.estado = 'aprobado_pendiente'
            reclamo.inspector_calidad = perfil
            reclamo.save(update_fields=['estado', 'inspector_calidad', 'updated_at'])
            
            HistorialEstado.objects.create(
                reclamo=reclamo, estado_anterior=estado_anterior, 
                estado_nuevo='aprobado_pendiente', usuario=perfil
            )
            messages.success(request, 'reclamo_aprobado')
            return redirect('detalle_reclamo', pk=reclamo.pk)

        if request.method == 'POST' and 'rechazar_reclamo' in request.POST:
            estado_anterior = reclamo.estado
            motivo_id = request.POST.get('motivo_rechazo')
            obs = request.POST.get('observaciones_calidad', '')
            
            reclamo.estado = 'rechazado'
            reclamo.inspector_calidad = perfil
            reclamo.observaciones_internas_calidad = obs
            if motivo_id:
                reclamo.motivo_rechazo_id = motivo_id
            reclamo.save()
            
            HistorialEstado.objects.create(
                reclamo=reclamo, estado_anterior=estado_anterior, 
                estado_nuevo='rechazado', usuario=perfil, comentarios=obs
            )
            messages.error(request, 'reclamo_rechazado')
            return redirect('detalle_reclamo', pk=reclamo.pk)

    # ==========================================
    # LÓGICA PARA ÁREAS OPERATIVAS (Resolver)
    # ==========================================
    elif perfil.departamento in ['poscosecha', 'produccion', 'exportaciones', 'ventas']:
        if request.method == 'POST':
            form = RespuestaForm(request.POST)
            if form.is_valid():
                respuesta = form.save(commit=False)
                respuesta.reclamo = reclamo
                respuesta.autor = perfil
                respuesta.save()

                if reclamo.estado == 'en_proceso':
                    reclamo.estado = 'resolucion_propuesta'
                    reclamo.save(update_fields=['estado'])
                    
                    HistorialEstado.objects.create(
                        reclamo=reclamo, estado_anterior='en_proceso', 
                        estado_nuevo='resolucion_propuesta', usuario=perfil
                    )

                messages.success(request, 'respuesta_enviada')
                return redirect('detalle_reclamo', pk=reclamo.pk)
        else:
            form = RespuestaForm()

    # Contexto para el template de calidad
    motivos_rechazo = MotivoRechazo.objects.filter(activo=True) if perfil.departamento == 'calidad' else None

    return render(request, 'reclamos/detalle_reclamo.html', {
        'reclamo': reclamo,
        'respuestas': respuestas,
        'evidencias': evidencias,
        'form': form,
        'perfil': perfil,
        'motivos_rechazo': motivos_rechazo,
    })


# =============================================
# PANEL DE CONTROL DE CALIDAD
# =============================================
@role_required('empleado')
def panel_calidad(request):
    perfil = request.user.perfil
    if perfil.departamento != 'calidad':
        messages.error(request, 'sin_permiso')
        return redirect('login')

    reclamos = Reclamo.objects.filter(
        estado__in=['pendiente_validacion', 'en_validacion']
    ).select_related('cliente__user', 'tipo_problema__categoria').order_by('-created_at')
    
    en_calidad_count = reclamos.count()

    return render(request, 'reclamos/panel_calidad.html', {
        'perfil': perfil,
        'reclamos': reclamos,
        'en_calidad_count': en_calidad_count,
    })


# =============================================
# PANEL GENÉRICO PARA EMPLEADOS (Ventas, Poscosecha, etc.)
# =============================================
@role_required('empleado')
def panel_empleado(request):
    perfil = request.user.perfil
    
    # Los reclamos que ya fueron aprobados y asignados a este departamento
    asignaciones = AsignacionArea.objects.filter(
        responsable=perfil
    ).select_related('reclamo__cliente__user').order_by('-reclamo__created_at')

    pendientes = asignaciones.filter(reclamo__estado='en_proceso').count()

    return render(request, 'reclamos/panel_empleado.html', {
        'perfil': perfil,
        'asignaciones': asignaciones,
        'pendientes': pendientes,
    })
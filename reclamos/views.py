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
import json


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

    # ==========================================
    # SEPARACIÓN DE CHATS (Público vs Interno)
    # ==========================================
    chat_externo = reclamo.respuestas.filter(es_interno=False).select_related('autor__user')
    chat_interno = None
    
    if perfil.role == 'empleado' and perfil.departamento in ['calidad', 'poscosecha', 'produccion', 'exportaciones']:
        chat_interno = reclamo.respuestas.filter(es_interno=True).select_related('autor__user')

    evidencias = reclamo.evidencias.all()
    form = None

    # ==========================================
    # LÓGICA PARA EL DEPARTAMENTO DE CALIDAD
    # ==========================================
    if perfil.departamento == 'calidad':
        
        # ---> ACCIÓN: APROBAR RECLAMO Y ASIGNAR A EMPLEADO <---
        if request.method == 'POST' and 'aprobar_reclamo' in request.POST:
            estado_anterior = reclamo.estado
            
            # 1. Cambiar estado a "En Proceso" porque ya hay alguien trabajando en ello
            reclamo.estado = 'en_proceso'
            reclamo.inspector_calidad = perfil
            reclamo.save(update_fields=['estado', 'inspector_calidad', 'updated_at'])
            
            HistorialEstado.objects.create(
                reclamo=reclamo, estado_anterior=estado_anterior, 
                estado_nuevo='en_proceso', usuario=perfil
            )

            # 2. SACAR AL EMPLEADO QUE MILENA ELIGIÓ EN EL HTML
            empleado_elegido_id = request.POST.get('empleado_asignado')
            from cuentas.models import Perfil as PerfilCuenta
            
            try:
                empleado_elegido = PerfilCuenta.objects.get(id=empleado_elegido_id)
                
                # 3. CREAR LA ASIGNACIÓN EN LA BASE DE DATOS
                AsignacionArea.objects.create(
                    reclamo=reclamo,
                    responsable=empleado_elegido,
                    departamento=empleado_elegido.get_departamento_display()
                )
                messages.success(request, 'reclamo_asignado')
            except PerfilCuenta.DoesNotExist:
                messages.error(request, 'error_asignacion')

            return redirect('detalle_reclamo', pk=reclamo.pk)

        # ---> ACCIÓN: RECHAZAR RECLAMO <---
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
    # LÓGICA PARA ÁREAS OPERATIVAS (Responder)
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

    # ==========================================
    # CONTEXTO PARA EL TEMPLATE HTML
    # ==========================================
    motivos_rechazo = MotivoRechazo.objects.filter(activo=True) if perfil.departamento == 'calidad' else None

    # Calcular a qué empleados se les puede asignar según el tipo de problema
    empleados_disponibles = None
    if perfil.departamento == 'calidad' and reclamo.estado == 'pendiente_validacion':
        categoria = reclamo.tipo_problema.categoria.nombre.lower()
        dept_destino = "produccion" # Por defecto
        
        if 'empaque' in categoria or 'contenido' in categoria:
            dept_destino = 'poscosecha'
        elif 'documentación' in categoria or 'identificación' in categoria:
            dept_destino = 'exportaciones'
            
        from cuentas.models import Perfil as PerfilCuenta
        empleados_disponibles = PerfilCuenta.objects.filter(
            departamento=dept_destino, 
            role='empleado',
            user__is_active=True
        )

    return render(request, 'reclamos/detalle_reclamo.html', {
        'reclamo': reclamo,
        'chat_externo': chat_externo,
        'chat_interno': chat_interno,
        'evidencias': evidencias,
        'form': form,
        'perfil': perfil,
        'motivos_rechazo': motivos_rechazo,
        'empleados_disponibles': empleados_disponibles, # <--- LA LÍNEA QUE FALTABA
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


@login_required
def panel_gerencia(request):
    # Seguridad: Solo superusuarios pueden ver esto
    if not request.user.is_superuser:
        return redirect('login')

    # 1. Traer TODOS los reclamos (optimizado para no saturar la BD)
    reclamos = Reclamo.objects.select_related(
        'cliente__user', 'inspector_calidad__user', 'tipo_problema'
    ).prefetch_related('areas_asignadas__responsable__user').order_by('-created_at')

    # 2. Calcular KPIs para las tarjetas
    total_reclamos = reclamos.count()
    pendientes_calidad = reclamos.filter(estado='pendiente_validacion').count()
    resueltos = reclamos.filter(estado__in=['resuelto', 'cerrado']).count()

    # 3. Datos para el GRÁFICO 1: Reclamos por Estado
    estados_data = Reclamo.objects.values('estado').annotate(total=Count('id'))
    estados_labels = [item['estado'].replace('_', ' ').title() for item in estados_data]
    estados_counts = [item['total'] for item in estados_data]

    # 4. Datos para el GRÁFICO 2: Reclamos por Departamento Asignado
    areas_data = AsignacionArea.objects.values('departamento').annotate(total=Count('reclamo', distinct=True))
    areas_labels = [item['departamento'] for item in areas_data]
    areas_counts = [item['total'] for item in areas_data]

    return render(request, 'reclamos/panel_gerencia.html', {
        'reclamos': reclamos,
        'total_reclamos': total_reclamos,
        'pendientes_calidad': pendientes_calidad,
        'resueltos': resueltos,
        'estados_labels': json.dumps(estados_labels),
        'estados_counts': json.dumps(estados_counts),
        'areas_labels': json.dumps(areas_labels),
        'areas_counts': json.dumps(areas_counts),
    })
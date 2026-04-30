import secrets
import string
from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import Perfil, AsignacionSecretaria
from .forms import LoginForm, RegistroClienteForm, CambiarPasswordForm



def generar_password_temporal(longitud=12):
    """Genera una contraseña segura que cumple las validaciones de Django."""
    caracteres = string.ascii_letters + string.digits + "!@#$%&*"
    while True:
        password = ''.join(secrets.choice(caracteres) for _ in range(longitud))
        if (any(c.islower() for c in password) and
            any(c.isupper() for c in password) and
            any(c.isdigit() for c in password) and
            any(c in "!@#$%&*" for c in password)):
            return password

# =============================================
# DECORADORES PERSONALIZADOS
# =============================================
def role_required(*roles):
    def decorator(view_func):
        @login_required
        def wrapper(request, *args, **kwargs):
            try:
                perfil = request.user.perfil
            except Perfil.DoesNotExist:
                logout(request)
                return redirect('login')

            if perfil.must_change_password:
                return redirect('cambiar_password')

            if perfil.role in roles:
                return view_func(request, *args, **kwargs)
            else:
                logout(request)
                messages.error(request, 'sin_permiso')
                return redirect('login')
        return wrapper
    return decorator


# =============================================
# LOGIN (Usa check_password en vez de authenticate)
# =============================================
def login_view(request):
    if request.user.is_authenticated:
        try:
            perfil = request.user.perfil
            if perfil.must_change_password:
                return redirect('cambiar_password')
            if perfil.role == 'cliente_comprador':
                return redirect('dashboard_cliente')
            elif perfil.role == 'secretaria':
                return redirect('panel_secretaria')
            elif perfil.role == 'vendedor':
                return redirect('registrar_cliente')
        except Perfil.DoesNotExist:
            logout(request)

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['username']
            password = form.cleaned_data['password']

            try:
                user = User.objects.get(email=email)
                perfil = user.perfil
            except (User.DoesNotExist, Perfil.DoesNotExist):
                messages.error(request, 'credenciales_invalidas')
                return render(request, 'cuentas/login.html', {'form': form})

            # Solo estos roles pueden usar el login
            if perfil.role not in ('cliente_comprador', 'secretaria', 'vendedor'):
                messages.error(request, 'credenciales_invalidas')
                return render(request, 'cuentas/login.html', {'form': form})

            # Verificar si la cuenta está bloqueada
            if perfil.is_locked:
                return render(request, 'cuentas/cuenta_bloqueada.html')

            # Verificar contraseña temporal expirada (solo clientes)
            if perfil.must_change_password and perfil.is_temp_password_expired:
                return render(request, 'cuentas/enlace_expirado.html')

            # Verificar contraseña directamente (sin authenticate)
            if not user.check_password(password):
                # Incrementar intentos fallidos
                perfil.failed_attempts += 1
                if perfil.failed_attempts >= 5:
                    perfil.locked_until = timezone.now() + timedelta(minutes=30)
                    perfil.save(update_fields=['failed_attempts', 'locked_until'])
                    return render(request, 'cuentas/cuenta_bloqueada.html')
                perfil.save(update_fields=['failed_attempts'])
                messages.error(request, 'credenciales_invalidas')
                return render(request, 'cuentas/login.html', {'form': form})

            # Verificar que esté activo
            if not user.is_active:
                messages.error(request, 'credenciales_invalidas')
                return render(request, 'cuentas/login.html', {'form': form})

            # Resetear intentos fallidos
            perfil.failed_attempts = 0
            perfil.save(update_fields=['failed_attempts'])

            # Iniciar sesión directamente
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            # Redirigir según rol
            if perfil.must_change_password:
                return redirect('cambiar_password')
            if perfil.role == 'cliente_comprador':
                return redirect('dashboard_cliente')
            if perfil.role == 'secretaria':
                return redirect('panel_secretaria')
            if perfil.role == 'vendedor':
                return redirect('registrar_cliente')
    else:
        form = LoginForm()

    return render(request, 'cuentas/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


# =============================================
# CAMBIAR CONTRASEÑA (Primer Ingreso)
# =============================================
@login_required
def cambiar_password_view(request):
    perfil = request.user.perfil

    if not perfil.must_change_password:
        if perfil.role == 'cliente_comprador':
            return redirect('dashboard_cliente')
        if perfil.role == 'secretaria':
            return redirect('panel_secretaria')
        if perfil.role == 'vendedor':
            return redirect('registrar_cliente')
        return redirect('login')

    if request.method == 'POST':
        form = CambiarPasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            perfil.must_change_password = False
            perfil.temp_password_expires_at = None
            perfil.failed_attempts = 0
            perfil.save(
                update_fields=[
                    'must_change_password',
                    'temp_password_expires_at',
                    'failed_attempts'
                ]
            )
            messages.success(request, 'password_actualizada')

            if perfil.role == 'cliente_comprador':
                return redirect('dashboard_cliente')
            if perfil.role == 'secretaria':
                return redirect('panel_secretaria')
            if perfil.role == 'vendedor':
                return redirect('registrar_cliente')
            return redirect('login')
    else:
        form = CambiarPasswordForm(user=request.user)

    return render(request, 'cuentas/cambiar_password.html', {'form': form})


# =============================================
# REGISTRAR CLIENTE (Solo Vendedores)
# =============================================
@role_required('vendedor')
def registrar_cliente_view(request):
    if request.method == 'POST':
        form = RegistroClienteForm(request.POST)
        if form.is_valid():
            temp_password = generar_password_temporal()

            user = User.objects.create_user(
                username=form.cleaned_data['email'],
                email=form.cleaned_data['email'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                password=temp_password,
                is_active=True
            )

            perfil = Perfil.objects.create(
                user=user,
                role='cliente_comprador',
                phone=form.cleaned_data.get('phone', ''),
                company_name=form.cleaned_data['company_name'],
                country=form.cleaned_data['country'],
                preferred_language=form.cleaned_data['preferred_language'],
                must_change_password=True,
                temp_password_expires_at=timezone.now() + timedelta(hours=72)
            )

            secretaria = form.cleaned_data['secretaria']
            AsignacionSecretaria.objects.create(
                secretaria=secretaria,
                cliente=perfil
            )

            enviar_credenciales_email(user, temp_password, perfil.preferred_language)

            messages.success(request, 'cliente_creado')
            form = RegistroClienteForm()
    else:
        form = RegistroClienteForm()

    clientes = Perfil.objects.filter(role='cliente_comprador').select_related('user').order_by('-created_at')
    asignaciones = AsignacionSecretaria.objects.filter(is_active=True).select_related('secretaria__user', 'cliente__user')

    return render(request, 'reclamos/registrar_cliente.html', {
        'form': form,
        'clientes': clientes,
        'asignaciones': asignaciones,
    })


# =============================================
# ENVIAR CORREO DE CREDENCIALES
# =============================================
def enviar_credenciales_email(user, temp_password, lang='es'):
    subject_map = {
        'es': 'Alexandra Farms — Sus credenciales de acceso',
        'en': 'Alexandra Farms — Your access credentials',
        'ru': 'Alexandra Farms — Ваши учётные данные',
    }

    nombre = user.first_name
    email = user.email

    html_message = render_to_string('cuentas/correo_credenciales.html', {
        'nombre': nombre,
        'email': email,
        'password': temp_password,
        'lang': lang,
        'login_url': settings.LOGIN_URL,
    })

    send_mail(
        subject=subject_map.get(lang, subject_map['es']),
        message='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        html_message=html_message,
        fail_silently=False,
    )
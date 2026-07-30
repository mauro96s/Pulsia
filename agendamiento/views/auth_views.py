from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.utils.crypto import get_random_string

from ..models.usuarios import CustomUser, RolUsuario
from ..models.pacientes import Paciente


# ────────────────────────────────────────────────────
# HU01 — Login
# ────────────────────────────────────────────────────
def login_view(request):
    """Autentica al usuario por correo/contraseña y redirige según su rol."""
    if request.user.is_authenticated:
        return _redirect_by_role(request.user)

    error = None
    correo_value = ''

    if request.method == 'POST':
        correo = request.POST.get('correo', '').strip()
        password = request.POST.get('password', '')
        correo_value = correo

        if not correo or not password:
            error = 'Por favor ingresa tu correo y contraseña.'
        else:
            # Django autentica usando USERNAME_FIELD='correo'
            user = authenticate(request, username=correo, password=password)
            if user is not None:
                if not user.estado_cuenta:
                    error = 'Tu cuenta está desactivada. Contacta al administrador.'
                else:
                    login(request, user)
                    messages.success(request, f'Bienvenido, {user.nombre_completo}.')
                    return _redirect_by_role(user)
            else:
                error = 'Correo o contraseña incorrectos. Verifica tus credenciales.'

    return render(request, 'agendamiento/auth/login.html', {
        'error': error,
        'correo_value': correo_value,
    })


def _redirect_by_role(user):
    """Redirección automática al panel según el rol del usuario."""
    rol = user.rol
    if rol == RolUsuario.ADMINISTRADOR:
        return redirect('dashboard_admin')
    elif rol == RolUsuario.RECEPCIONISTA:
        return redirect('dashboard_recepcionista')
    elif rol == RolUsuario.ESPECIALISTA:
        return redirect('dashboard_especialista')
    elif rol == RolUsuario.PACIENTE:
        return redirect('dashboard_paciente')
    else:
        return redirect('login')


# ────────────────────────────────────────────────────
# Logout
# ────────────────────────────────────────────────────
def logout_view(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente.')
    return redirect('login')


# ────────────────────────────────────────────────────
# Registro de Paciente
# ────────────────────────────────────────────────────
def register_view(request):
    """Crea una cuenta de tipo Paciente con perfil asociado."""
    if request.user.is_authenticated:
        return _redirect_by_role(request.user)

    error = None
    form_data = {}

    if request.method == 'POST':
        nombre_completo  = request.POST.get('nombre_completo', '').strip()
        correo           = request.POST.get('correo', '').strip().lower()
        telefono         = request.POST.get('telefono', '').strip()
        fecha_nacimiento = request.POST.get('fecha_nacimiento', '').strip()
        password1        = request.POST.get('password1', '')
        password2        = request.POST.get('password2', '')
        acepta_habeas    = request.POST.get('acepta_habeas_data') == 'on'

        form_data = {
            'nombre_completo': nombre_completo,
            'correo': correo,
            'telefono': telefono,
            'fecha_nacimiento': fecha_nacimiento,
        }

        # Validaciones de servidor
        if not all([nombre_completo, correo, fecha_nacimiento, password1, password2]):
            error = 'Todos los campos obligatorios deben ser completados.'
        elif password1 != password2:
            error = 'Las contraseñas no coinciden.'
        elif len(password1) < 8:
            error = 'La contraseña debe tener al menos 8 caracteres.'
        elif not acepta_habeas:
            error = 'Debes aceptar el tratamiento de datos personales (Habeas Data).'
        elif CustomUser.objects.filter(correo=correo).exists():
            error = 'Ya existe una cuenta registrada con ese correo electrónico.'
        else:
            try:
                # Crear usuario — username único automático
                user = CustomUser.objects.create_user(
                    username=correo,
                    correo=correo,
                    email=correo,
                    nombre_completo=nombre_completo,
                    rol=RolUsuario.PACIENTE,
                    telefono=telefono,
                    password=password1,
                )
                # Crear perfil Paciente
                Paciente.objects.create(
                    usuario=user,
                    fecha_nacimiento=fecha_nacimiento,
                    acepta_habeas_data=acepta_habeas,
                )
                login(request, user)
                messages.success(request, f'¡Bienvenido a Pulsia, {nombre_completo}! Tu cuenta ha sido creada.')
                return redirect('dashboard_paciente')
            except Exception as e:
                error = f'Ocurrió un error al crear tu cuenta. Intenta nuevamente.'

    return render(request, 'agendamiento/auth/register.html', {
        'error': error,
        'form_data': form_data,
    })

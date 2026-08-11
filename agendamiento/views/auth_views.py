from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from agendamiento.models import CustomUser, Paciente, RolUsuario, TipoDocumento
from datetime import datetime

def login_view(request):
    """Vista de Login con autenticación y redirección automática por rol (HU01)."""
    # Si el usuario ya está autenticado, redirigir según su rol
    if request.user.is_authenticated:
        return redirect_by_role(request.user)

    if request.method == 'POST':
        correo = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        # Buscar usuario por correo
        try:
            user_obj = CustomUser.objects.get(correo=correo)
            user = authenticate(request, username=user_obj.username, password=password)
        except CustomUser.DoesNotExist:
            user = None

        if user is not None:
            if not user.is_active or not user.estado_cuenta:
                messages.error(request, 'Tu cuenta se encuentra desactivada. Contacta al administrador.')
                return render(request, 'agendamiento/auth/login.html')

            login(request, user)
            return redirect_by_role(user)
        else:
            messages.error(request, 'Correo electrónico o contraseña incorrectos.')

    return render(request, 'agendamiento/auth/login.html')


def register_view(request):
    """Vista de Registro exclusiva para Pacientes (HU02 / HU10)."""
    if request.user.is_authenticated:
        return redirect_by_role(request.user)

    if request.method == 'POST':
        nombre_completo = request.POST.get('nombre_completo', '').strip()
        tipo_documento = request.POST.get('tipo_documento', TipoDocumento.CC)
        num_documento = request.POST.get('num_documento', '').strip()
        correo = request.POST.get('correo', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        fecha_nac_str = request.POST.get('fecha_nacimiento', '')
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        acepta_habeas = request.POST.get('acepta_habeas_data') == 'on'

        # Validaciones
        if password != password_confirm:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'agendamiento/auth/register.html')

        if CustomUser.objects.filter(correo=correo).exists():
            messages.error(request, 'Ya existe un usuario registrado con este correo electrónico.')
            return render(request, 'agendamiento/auth/register.html')

        if num_documento and CustomUser.objects.filter(num_documento=num_documento).exists():
            messages.error(request, 'Ya existe un usuario registrado con este número de documento.')
            return render(request, 'agendamiento/auth/register.html')

        try:
            fecha_nacimiento = datetime.strptime(fecha_nac_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Fecha de nacimiento inválida.')
            return render(request, 'agendamiento/auth/register.html')

        # Crear Usuario con rol PACIENTE
        user = CustomUser.objects.create_user(
            username=correo,
            correo=correo,
            nombre_completo=nombre_completo,
            tipo_documento=tipo_documento,
            num_documento=num_documento,
            telefono=telefono,
            rol=RolUsuario.PACIENTE,
            password=password
        )

        # Crear Perfil Paciente
        Paciente.objects.create(
            usuario=user,
            fecha_nacimiento=fecha_nacimiento,
            acepta_habeas_data=acepta_habeas
        )

        login(request, user)
        messages.success(request, '¡Registro completado exitosamente! Bienvenido a tu Portal de Salud.')
        return redirect('dashboard_paciente')

    return render(request, 'agendamiento/auth/register.html')


def logout_view(request):
    """Cierra la sesión del usuario."""
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente.')
    return redirect('login')


def redirect_by_role(user):
    """Auxiliar para redirigir al dashboard según el rol del usuario."""
    if user.rol == RolUsuario.ADMINISTRADOR:
        return redirect('dashboard_admin')
    elif user.rol == RolUsuario.RECEPCIONISTA:
        return redirect('dashboard_recepcion')
    elif user.rol == RolUsuario.ESPECIALISTA:
        return redirect('dashboard_especialista')
    elif user.rol == RolUsuario.PACIENTE:
        return redirect('dashboard_paciente')
    return redirect('dashboard')

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from ..models.usuarios import RolUsuario


def dashboard_view(request):
    """Redirige al dashboard correspondiente según el rol del usuario."""
    if not request.user.is_authenticated:
        return redirect('login')

    rol = request.user.rol
    if rol == RolUsuario.ADMINISTRADOR:
        return redirect('dashboard_admin')
    elif rol == RolUsuario.RECEPCIONISTA:
        return redirect('dashboard_recepcionista')
    elif rol == RolUsuario.ESPECIALISTA:
        return redirect('dashboard_especialista')
    elif rol == RolUsuario.PACIENTE:
        return redirect('dashboard_paciente')
    return redirect('login')


@login_required(login_url='login')
def admin_dashboard_view(request):
    """Panel del Administrador — HU11, HU12."""
    if request.user.rol != RolUsuario.ADMINISTRADOR:
        messages.error(request, 'No tienes permiso para acceder a esa página.')
        return redirect('login')

    # KPIs — se pueden reemplazar con queries reales
    from ..models.usuarios import CustomUser
    from ..models.pacientes import Paciente

    context = {
        'kpi_citas': 0,           # TODO: Cita.objects.filter(fecha=today).count()
        'kpi_especialistas': CustomUser.objects.filter(rol=RolUsuario.ESPECIALISTA, estado_cuenta=True).count(),
        'kpi_pacientes': Paciente.objects.count(),
        'kpi_ausencias': 0,       # TODO: AusenciaPermiso.objects.filter(estado='Pendiente').count()
    }
    return render(request, 'agendamiento/dashboard/admin_dashboard.html', context)


@login_required(login_url='login')
def recepcionista_dashboard_view(request):
    """Panel del Recepcionista — HU06, HU07, HU14."""
    allowed = [RolUsuario.RECEPCIONISTA, RolUsuario.ADMINISTRADOR]
    if request.user.rol not in allowed:
        messages.error(request, 'No tienes permiso para acceder a esa página.')
        return redirect('login')

    context = {}
    return render(request, 'agendamiento/dashboard/recepcionista_dashboard.html', context)


@login_required(login_url='login')
def especialista_dashboard_view(request):
    """Panel del Especialista — HU04, HU05, HU13."""
    if request.user.rol != RolUsuario.ESPECIALISTA:
        messages.error(request, 'No tienes permiso para acceder a esa página.')
        return redirect('login')

    context = {
        'turno_activo': False,    # TODO: Turno.objects.filter(especialista=user, fecha=today, estado='Presente').exists()
        'citas_programadas': 0,
        'citas_atendidas': 0,
        'citas_pendientes': 0,
    }
    return render(request, 'agendamiento/dashboard/especialista_dashboard.html', context)


@login_required(login_url='login')
def paciente_dashboard_view(request):
    """Panel del Paciente — HU02, HU03, HU09 con RN04."""
    if request.user.rol != RolUsuario.PACIENTE:
        messages.error(request, 'No tienes permiso para acceder a esa página.')
        return redirect('login')

    try:
        perfil = request.user.perfil_paciente
        penalizado = perfil.contador_inasistencias >= 3  # RN04
    except Exception:
        perfil = None
        penalizado = False

    context = {
        'paciente_penalizado': penalizado,
        'proxima_cita': None,     # TODO: Cita.objects.filter(paciente=perfil, estado='Programada').order_by('fecha_hora').first()
    }
    return render(request, 'agendamiento/dashboard/paciente_dashboard.html', context)

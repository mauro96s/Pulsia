from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from agendamiento.views.auth_views import redirect_by_role
from agendamiento.models import (
    Cita, EstadoCita, Paciente, Especialista, Especialidad, ListaEspera, RolUsuario
)
import json

@login_required(login_url='login')
def dashboard_view(request):
    """Vista principal router: Redirige automáticamente al dashboard del rol del usuario."""
    return redirect_by_role(request.user)

from agendamiento.views.admin_views import admin_dashboard_view
from agendamiento.views.citas_views import recepcion_dashboard_view
from agendamiento.views.especialistas_views import especialista_dashboard_view


def _generar_eventos_fullcalendar(citas_qs):
    """Genera JSON estructurado de eventos para FullCalendar.js."""
    eventos = []
    for c in citas_qs:
        color = '#3B82F6'
        if c.estado_cita == 'Atendida':
            color = '#10B981'
        elif c.estado_cita == 'Cancelada':
            color = '#EF4444'
        elif c.estado_cita == 'No_Asistio':
            color = '#6B7280'
        elif c.estado_cita == 'En_Sala':
            color = '#F59E0B'
        elif c.estado_cita == 'Pendiente_Reubicacion':
            color = '#8B5CF6'

        paciente_nombre = c.paciente.usuario.nombre_completo if hasattr(c, 'paciente') and c.paciente and hasattr(c.paciente, 'usuario') else 'Paciente'
        especialista_nombre = c.especialista.usuario.nombre_completo if hasattr(c, 'especialista') and c.especialista and hasattr(c.especialista, 'usuario') else 'Médico'
        consultorio_nombre = c.consultorio.nombre_codigo if hasattr(c, 'consultorio') and c.consultorio else 'N/A'

        eventos.append({
            'id': c.id,
            'title': f"{paciente_nombre} - Dr. {especialista_nombre} ({consultorio_nombre})",
            'start': c.fecha_hora_inicio.isoformat() if c.fecha_hora_inicio else '',
            'end': c.fecha_hora_fin.isoformat() if c.fecha_hora_fin else '',
            'color': color,
            'extendedProps': {
                'estado': c.get_estado_cita_display() if hasattr(c, 'get_estado_cita_display') else c.estado_cita,
                'paciente': paciente_nombre,
                'especialista': especialista_nombre,
                'consultorio': consultorio_nombre
            }
        })
    return json.dumps(eventos)


@login_required(login_url='login')
def paciente_dashboard_view(request):
    """
    Dashboard del Paciente (HU02, HU03, HU09, HU07, RN01, RN02, RN04).
    Carga dinámicamente las citas activas, el historial clínico, contadores de inasistencia y formularios de lista de espera.
    """
    if request.user.rol != RolUsuario.PACIENTE:
        return redirect_by_role(request.user)

    paciente = getattr(request.user, 'perfil_paciente', None)
    if not paciente:
        paciente = Paciente.objects.filter(usuario=request.user).first()

    if not paciente:
        messages.error(request, "Perfil de paciente no encontrado. Contacta a soporte.")
        return redirect('login')

    # 1. Citas Próximas Activas
    citas_activas = Cita.objects.select_related(
        'especialista__usuario', 'especialista__especialidad', 'consultorio'
    ).filter(
        paciente=paciente,
        estado_cita__in=[EstadoCita.PROGRAMADA, EstadoCita.EN_SALA, EstadoCita.PENDIENTE_REUBICACION]
    ).order_by('fecha_hora_inicio')

    # 2. Historial de Citas Pasadas
    citas_historial = Cita.objects.select_related(
        'especialista__usuario', 'especialista__especialidad', 'consultorio'
    ).filter(
        paciente=paciente,
        estado_cita__in=[EstadoCita.ATENDIDA, EstadoCita.CANCELADA, EstadoCita.NO_ASISTIO]
    ).order_by('-fecha_hora_inicio')

    # 3. Lista de Espera del Paciente
    listas_espera = ListaEspera.objects.select_related(
        'especialidad', 'especialista__usuario'
    ).filter(paciente=paciente).order_by('-fecha_registro')

    # 4. Catálogos para Modales
    especialidades = Especialidad.objects.all()
    especialistas = Especialista.objects.select_related('usuario', 'especialidad').filter(usuario__estado_cuenta=True)

    inasistencias = getattr(paciente, 'inasistencias_acumuladas', 0)
    bloqueado = getattr(paciente, 'bloqueado_agendamiento_web', False) or (inasistencias >= 3)

    context = {
        'paciente': paciente,
        'citas_activas': citas_activas,
        'citas_historial': citas_historial,
        'listas_espera': listas_espera,
        'cant_activas': citas_activas.count(),
        'especialidades': especialidades,
        'especialistas': especialistas,
        'inasistencias_acumuladas': inasistencias,
        'bloqueado_agendamiento_web': bloqueado,
        'EstadoCita': EstadoCita
    }

    return render(request, 'agendamiento/dashboard/paciente.html', context)

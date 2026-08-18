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


from django.db.models import Q

@login_required(login_url='login')
def paciente_dashboard_view(request):
    """
    Vista 'Mis Citas' del Paciente.
    Muestra el encabezado de módulo, barra de búsqueda y filtros en 12 columnas, y la tabla completa de citas.
    """
    if request.user.rol != RolUsuario.PACIENTE:
        return redirect_by_role(request.user)

    paciente = getattr(request.user, 'perfil_paciente', None)
    if not paciente:
        paciente = Paciente.objects.filter(usuario=request.user).first()

    if not paciente:
        messages.error(request, "Perfil de paciente no encontrado. Contacta a soporte.")
        return redirect('login')

    query = request.GET.get('q', '').strip()
    estado_filtro = request.GET.get('estado', '').strip()

    citas_qs = Cita.objects.select_related(
        'especialista__usuario', 'especialista__especialidad', 'consultorio'
    ).filter(paciente=paciente).order_by('-fecha_hora_inicio')

    if query:
        citas_qs = citas_qs.filter(
            Q(especialista__usuario__nombre_completo__icontains=query) |
            Q(especialista__especialidad__nombre_especialidad__icontains=query)
        )

    if estado_filtro:
        citas_qs = citas_qs.filter(estado_cita=estado_filtro)

    # 1. Citas Próximas Activas (sin filtro) para contadores
    citas_activas = Cita.objects.filter(
        paciente=paciente,
        estado_cita__in=[EstadoCita.PROGRAMADA, EstadoCita.EN_SALA, EstadoCita.PENDIENTE_REUBICACION]
    )

    # 2. Lista de Espera del Paciente
    listas_espera = ListaEspera.objects.select_related(
        'especialidad', 'especialista__usuario'
    ).filter(paciente=paciente).order_by('-fecha_registro')

    # 3. Catálogos para Modales
    especialidades = Especialidad.objects.all()
    especialistas = Especialista.objects.select_related('usuario', 'especialidad').filter(usuario__estado_cuenta=True)

    inasistencias = getattr(paciente, 'contador_inasistencias', 0)
    bloqueado = getattr(paciente, 'bloqueado_agendamiento_web', False) or (inasistencias >= 3)

    context = {
        'paciente': paciente,
        'citas': citas_qs,
        'citas_activas': citas_activas,
        'cant_activas': citas_activas.count(),
        'listas_espera': listas_espera,
        'especialidades': especialidades,
        'especialistas': especialistas,
        'inasistencias_acumuladas': inasistencias,
        'bloqueado_agendamiento_web': bloqueado,
        'query': query,
        'estado_filtro': estado_filtro,
        'EstadoCita': EstadoCita
    }

    return render(request, 'agendamiento/dashboard/paciente.html', context)

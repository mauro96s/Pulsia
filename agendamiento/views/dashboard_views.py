import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q

from ..models.usuarios import CustomUser, RolUsuario
from ..models.pacientes import Paciente
from ..models.especialistas import Especialidad, Consultorio, Especialista, EstadoTurno
from ..models.citas import Cita, EstadoCita, AusenciasPermisos, EstadoAprobacion, ListaEspera


STATUS_COLORS = {
    EstadoCita.PROGRAMADA: '#0056b3',
    EstadoCita.EN_SALA: '#d97706',
    EstadoCita.ATENDIDA: '#059669',
    EstadoCita.NO_ASISTIO: '#dc2626',
    EstadoCita.PENDIENTE_REUBICACION: '#7c3aed',
    EstadoCita.CANCELADA: '#6b7280',
}


def _generar_eventos_fullcalendar(citas_qs):
    events = []
    for c in citas_qs:
        color = STATUS_COLORS.get(c.estado_cita, '#0056b3')
        events.append({
            'id': c.id,
            'title': f"{c.paciente.usuario.nombre_completo} · Dr/Dra. {c.especialista.usuario.nombre_completo}",
            'start': c.fecha_hora_inicio.isoformat(),
            'end': c.fecha_hora_fin.isoformat(),
            'backgroundColor': color,
            'borderColor': color,
            'textColor': '#ffffff',
            'extendedProps': {
                'especialista_id': c.especialista.id if c.especialista else '',
                'paciente_cedula': c.paciente.usuario.username if (c.paciente and c.paciente.usuario) else '',
                'paciente': c.paciente.usuario.nombre_completo if (c.paciente and c.paciente.usuario) else '',
                'especialista': c.especialista.usuario.nombre_completo if (c.especialista and c.especialista.usuario) else '',
                'especialidad': c.especialista.especialidad.nombre_especialidad if (c.especialista and c.especialista.especialidad) else '',
                'consultorio': c.consultorio.nombre_codigo if c.consultorio else '',
                'estado': c.get_estado_cita_display(),
                'estado_code': c.estado_cita,
                'notas': c.notas_clinicas or ''
            }
        })
    return json.dumps(events)


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
    """Panel del Administrador — HU08, HU11 (BI), HU12 (CRUD)."""
    if request.user.rol != RolUsuario.ADMINISTRADOR:
        messages.error(request, 'No tienes permiso para acceder a esa página.')
        return redirect('login')

    hoy = timezone.now().date()
    from ..services.festivos_service import FESTIVOS_FIJOS, FESTIVOS_EMILIANI

    # KPIs
    kpi_citas = Cita.objects.filter(fecha_hora_inicio__date=hoy).count()
    kpi_especialistas = Especialista.objects.filter(usuario__estado_cuenta=True).count()
    kpi_pacientes = Paciente.objects.count()
    kpi_ausencias = AusenciasPermisos.objects.filter(estado_aprobacion=EstadoAprobacion.PENDIENTE).count()

    # Reportes BI (HU11)
    total_citas = Cita.objects.count()
    total_no_asistio = Cita.objects.filter(estado_cita=EstadoCita.NO_ASISTIO).count()
    tasa_inasistencia = round((total_no_asistio / total_citas * 100), 1) if total_citas > 0 else 0.0

    demandas_especialidad = Especialidad.objects.annotate(
        num_citas=Count('especialistas__citas')
    ).order_by('-num_citas')

    ausencias_pendientes = AusenciasPermisos.objects.filter(
        estado_aprobacion=EstadoAprobacion.PENDIENTE
    ).order_by('fecha_hora_inicio')

    todas_las_citas = Cita.objects.select_related('paciente__usuario', 'especialista__usuario', 'especialista__especialidad', 'consultorio').all()

    context = {
        'kpi_citas': kpi_citas,
        'kpi_especialistas': kpi_especialistas,
        'kpi_pacientes': kpi_pacientes,
        'kpi_ausencias': kpi_ausencias,
        'tasa_inasistencia': tasa_inasistencia,
        'total_citas': total_citas,
        'total_no_asistio': total_no_asistio,
        'demandas_especialidad': demandas_especialidad,
        'ausencias_pendientes': ausencias_pendientes,
        'especialidades': Especialidad.objects.all(),
        'consultorios': Consultorio.objects.all(),
        'especialistas': Especialista.objects.select_related('usuario', 'especialidad').all(),
        'festivos_fijos': FESTIVOS_FIJOS,
        'festivos_emiliani': FESTIVOS_EMILIANI,
        'fullcalendar_events_json': _generar_eventos_fullcalendar(todas_las_citas),
    }
    return render(request, 'agendamiento/dashboard/admin_dashboard.html', context)


@login_required(login_url='login')
def recepcionista_dashboard_view(request):
    """Panel del Recepcionista — HU06, HU07, HU14."""
    allowed = [RolUsuario.RECEPCIONISTA, RolUsuario.ADMINISTRADOR]
    if request.user.rol not in allowed:
        messages.error(request, 'No tienes permiso para acceder a esa página.')
        return redirect('login')

    # RN03: Auto-marcar No Asistió tras 15 minutos de retraso sobre la hora de la cita
    ahora_actual = timezone.now()
    limite_tolerancia_15m = ahora_actual - timezone.timedelta(minutes=15)
    citas_vencidas = Cita.objects.filter(
        estado_cita=EstadoCita.PROGRAMADA,
        fecha_hora_inicio__lt=limite_tolerancia_15m
    )
    for c_venc in citas_vencidas:
        c_venc.estado_cita = EstadoCita.NO_ASISTIO
        c_venc.save()
        if c_venc.paciente:
            c_venc.paciente.contador_inasistencias += 1
            c_venc.paciente.save()

    # Filtro por fecha (por defecto hoy)
    fecha_filtro_str = request.GET.get('fecha')
    if fecha_filtro_str:
        try:
            fecha_filtro = timezone.datetime.strptime(fecha_filtro_str, '%Y-%m-%d').date()
        except ValueError:
            fecha_filtro = timezone.now().date()
    else:
        fecha_filtro = timezone.now().date()

    citas_hoy = Cita.objects.filter(
        fecha_hora_inicio__date=fecha_filtro
    ).select_related('paciente__usuario', 'especialista__usuario', 'especialista__especialidad', 'consultorio').order_by('fecha_hora_inicio')

    # Citas prioritarias por reubicar (HU14 / RN08)
    citas_prioritarias = Cita.objects.filter(
        estado_cita=EstadoCita.PENDIENTE_REUBICACION
    ).select_related('paciente__usuario', 'especialista__usuario', 'especialista__especialidad').order_by('fecha_hora_inicio')

    especialistas_hoy = Especialista.objects.select_related('usuario', 'especialidad').all()
    pacientes = Paciente.objects.select_related('usuario').all()
    consultorios = Consultorio.objects.filter(estado_operativo=True)
    listas_espera = ListaEspera.objects.select_related('paciente__usuario', 'especialista__usuario').filter(estado='Pendiente')

    todas_citas_recepcion = Cita.objects.select_related('paciente__usuario', 'especialista__usuario', 'especialista__especialidad', 'consultorio').all()

    context = {
        'fecha_filtro': fecha_filtro.strftime('%Y-%m-%d'),
        'citas_hoy': citas_hoy,
        'citas_prioritarias': citas_prioritarias,
        'especialistas_hoy': especialistas_hoy,
        'pacientes': pacientes,
        'consultorios': consultorios,
        'listas_espera': listas_espera,
        'estados_cita': EstadoCita.choices,
        'fullcalendar_events_json': _generar_eventos_fullcalendar(todas_citas_recepcion),
    }
    return render(request, 'agendamiento/dashboard/recepcionista_dashboard.html', context)


@login_required(login_url='login')
def especialista_dashboard_view(request):
    """Panel del Especialista — HU04, HU05, HU13."""
    if request.user.rol != RolUsuario.ESPECIALISTA:
        messages.error(request, 'No tienes permiso para acceder a esa página.')
        return redirect('login')

    especialista = getattr(request.user, 'perfil_especialista', None)
    hoy = timezone.now().date()
    inicio_semana = hoy - timezone.timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timezone.timedelta(days=6)

    if especialista:
        turno_activo = (especialista.estado_turno == EstadoTurno.PRESENTE)
        citas_hoy = Cita.objects.filter(
            especialista=especialista,
            fecha_hora_inicio__date=hoy
        ).select_related('paciente__usuario', 'consultorio').order_by('fecha_hora_inicio')

        citas_semana = Cita.objects.filter(
            especialista=especialista,
            fecha_hora_inicio__date__gte=inicio_semana,
            fecha_hora_inicio__date__lte=fin_semana
        ).select_related('paciente__usuario', 'consultorio').order_by('fecha_hora_inicio')

        citas_todas_especialista = Cita.objects.filter(
            especialista=especialista
        ).select_related('paciente__usuario', 'consultorio', 'especialista__usuario', 'especialista__especialidad').order_by('fecha_hora_inicio')

        citas_programadas = citas_hoy.filter(estado_cita=EstadoCita.PROGRAMADA).count()
        citas_atendidas = citas_hoy.filter(estado_cita=EstadoCita.ATENDIDA).count()
        citas_pendientes = citas_hoy.filter(estado_cita__in=[EstadoCita.PROGRAMADA, EstadoCita.EN_SALA]).count()

        mis_permisos = AusenciasPermisos.objects.filter(especialista=especialista).order_by('-fecha_hora_inicio')
        # RN06: Historial de pacientes atendidos por este médico
        historial_atendidas = Cita.objects.filter(
            especialista=especialista,
            estado_cita=EstadoCita.ATENDIDA
        ).select_related('paciente__usuario').order_by('-fecha_hora_inicio')
    else:
        turno_activo = False
        citas_hoy = []
        citas_semana = []
        citas_todas_especialista = []
        citas_programadas = 0
        citas_atendidas = 0
        citas_pendientes = 0
        mis_permisos = []
        historial_atendidas = []

    context = {
        'especialista': especialista,
        'turno_activo': turno_activo,
        'citas_hoy': citas_hoy,
        'citas_semana': citas_semana,
        'citas_programadas': citas_programadas,
        'citas_atendidas': citas_atendidas,
        'citas_pendientes': citas_pendientes,
        'mis_permisos': mis_permisos,
        'historial_atendidas': historial_atendidas,
        'fullcalendar_events_json': _generar_eventos_fullcalendar(citas_todas_especialista),
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

    ahora = timezone.now()
    if perfil:
        citas = Cita.objects.filter(
            paciente=perfil
        ).select_related('especialista__usuario', 'especialista__especialidad', 'consultorio').order_by('-fecha_hora_inicio')

        proxima_cita = citas.filter(
            estado_cita=EstadoCita.PROGRAMADA,
            fecha_hora_inicio__gte=ahora
        ).first()

        historial_notas = citas.filter(
            estado_cita=EstadoCita.ATENDIDA
        ).exclude(notas_clinicas__isnull=True).exclude(notas_clinicas__exact='')
    else:
        citas = []
        proxima_cita = None
        historial_notas = []

    context = {
        'paciente': perfil,
        'paciente_penalizado': penalizado,
        'proxima_cita': proxima_cita,
        'citas': citas,
        'historial_notas': historial_notas,
        'especialidades': Especialidad.objects.all(),
        'especialistas': Especialista.objects.select_related('usuario', 'especialidad').all(),
    }
    return render(request, 'agendamiento/dashboard/paciente_dashboard.html', context)

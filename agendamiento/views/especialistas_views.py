"""
Controladores / Vistas para la gestión del Rol Especialista Médico (Pulsia Medical Systems).
Cumple con las reglas de negocio RN-ESP-01 a RN-ESP-10:
- RN-ESP-01: Privacidad de la Agenda del Especialista.
- RN-ESP-02: Anticipación Mínima de 24 Horas para Solicitud de Ausencias.
- RN-ESP-04: Flujo de Atención Operado por Recepción (Sólo "Finalizar Atención").
- RN-ESP-08: Privacidad del Historial Clínico.
- RN-ESP-09: Cierre Extemporáneo de Notas Clínicas (Plazo de 48 Horas / Notas Selladas).
- RN-ESP-10: Agendamiento Directo de Citas de Control.
"""

from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone

from agendamiento.models import (
    Especialista, Cita, EstadoCita, EstadoTurno, AusenciasPermisos,
    EstadoAprobacion, RolUsuario
)
from agendamiento.services import (
    marcar_checkin_medico,
    atender_y_guardar_notas_cita,
    solicitar_permiso_especialista,
    agendar_cita_web
)


def es_especialista_o_admin(user) -> bool:
    return user.is_authenticated and user.rol in [RolUsuario.ESPECIALISTA, RolUsuario.ADMINISTRADOR]


def obtener_perfil_especialista(user):
    """Auxiliar para obtener el perfil médico del usuario autenticado."""
    if hasattr(user, 'perfil_especialista'):
        return user.perfil_especialista
    return Especialista.objects.select_related('usuario', 'especialidad', 'consultorio').first()


@login_required(login_url='login')
def especialista_dashboard_view(request):
    """
    Dashboard del Especialista Médico (RN-ESP-01, RN-ESP-04, RN-ESP-08, RN-ESP-09).
    Muestra únicamente las citas propias y las notas selladas >48h.
    """
    if not es_especialista_o_admin(request.user):
        messages.error(request, "Acceso no autorizado al panel del especialista.")
        return redirect('dashboard')

    especialista = obtener_perfil_especialista(request.user)

    if not especialista:
        messages.warning(request, "Tu cuenta no tiene un perfil médico asignado. Contacta al administrador.")
        return redirect('dashboard')

    # 1. Filtro de Fecha
    fecha_str = request.GET.get('fecha', '')
    if fecha_str:
        try:
            fecha_sel = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            fecha_sel = timezone.now().date()
    else:
        fecha_sel = timezone.now().date()

    # 2. Citas del Especialista (RN-ESP-01: Privacidad Estricta de Agenda)
    inicio_dia = timezone.make_aware(datetime.combine(fecha_sel, datetime.min.time()))
    fin_dia = timezone.make_aware(datetime.combine(fecha_sel, datetime.max.time()))

    citas_qs = Cita.objects.select_related(
        'paciente__usuario', 'consultorio', 'especialista__especialidad'
    ).filter(
        especialista=especialista,
        fecha_hora_inicio__gte=inicio_dia,
        fecha_hora_inicio__lte=fin_dia
    ).order_by('fecha_hora_inicio')

    ahora = timezone.now()
    citas_list = []
    for c in citas_qs:
        # RN-ESP-09: Cierre Extemporáneo de Notas Clínicas (Plazo de 48 Horas)
        diferencia_horas = (ahora - c.fecha_hora_inicio).total_seconds() / 3600.0 if c.fecha_hora_inicio else 0
        c.puede_editar_notas = (c.estado_cita == EstadoCita.ATENDIDA and diferencia_horas <= 48) or c.estado_cita == EstadoCita.EN_SALA
        c.notas_selladas = (c.estado_cita == EstadoCita.ATENDIDA and diferencia_horas > 48)
        citas_list.append(c)

    # Contadores por Estado
    cant_total = len(citas_list)
    cant_en_sala = sum(1 for c in citas_list if c.estado_cita == EstadoCita.EN_SALA)
    cant_atendidas = sum(1 for c in citas_list if c.estado_cita == EstadoCita.ATENDIDA)

    # 3. Solicitudes de Permiso
    permisos = AusenciasPermisos.objects.filter(especialista=especialista).order_by('-fecha_hora_inicio')[:10]

    # RN-ESP-10: Especialidades con seguimiento obligatorio de control
    especialidad_nombre = especialista.especialidad.nombre_especialidad if especialista.especialidad else ''
    es_seguimiento_control = especialidad_nombre in ['Ginecología', 'Psicología', 'Medicina General', 'Pediatría']

    # Pacientes para el filtro de la agenda (Calendario)
    from agendamiento.models import Paciente
    pacientes_ids = Cita.objects.filter(especialista=especialista).values_list('paciente_id', flat=True).distinct()
    pacientes = Paciente.objects.select_related('usuario').filter(
        id__in=pacientes_ids,
        usuario__estado_cuenta=True
    ).order_by('usuario__nombre_completo')

    context = {
        'especialista': especialista,
        'fecha_seleccionada': fecha_sel.strftime('%Y-%m-%d'),
        'fecha_actual_display': fecha_sel,
        'citas': citas_list,
        'cant_total': cant_total,
        'cant_en_sala': cant_en_sala,
        'cant_atendidas': cant_atendidas,
        'permisos': permisos,
        'es_seguimiento_control': es_seguimiento_control,
        'pacientes': pacientes,
        'EstadoCita': EstadoCita,
        'EstadoTurno': EstadoTurno,
        'EstadoAprobacion': EstadoAprobacion,
    }

    return render(request, 'agendamiento/dashboard/especialista.html', context)


@login_required(login_url='login')
@require_POST
def especialista_checkin_turno_view(request):
    """Auxiliar legacy de conmutación de turno."""
    messages.info(request, "El turno médico es registrado únicamente por Recepción al ingresar al centro médico.")
    return redirect('dashboard_especialista')


@login_required(login_url='login')
@require_POST
def especialista_atender_cita_view(request, cita_id):
    """
    HU05 / RN-ESP-04 / RN-ESP-10: Finalizar Atención e Ingresar Notas Clínicas.
    Cambia la cita de 'EN_SALA' a 'ATENDIDA'.
    Si se marca la opción de 'Cita de Control Directo' (RN-ESP-10), agendar automáticamente la cita de seguimiento.
    """
    especialista = obtener_perfil_especialista(request.user)
    if not especialista:
        messages.error(request, "Perfil médico no encontrado.")
        return redirect('dashboard_especialista')

    notas_clinicas = request.POST.get('notas_clinicas', '').strip()
    agendar_control = request.POST.get('agendar_control') == 'on'
    fecha_control_str = request.POST.get('fecha_control', '')
    hora_control_str = request.POST.get('hora_control', '09:00')

    try:
        cita = atender_y_guardar_notas_cita(cita_id, especialista, notas_clinicas)
        msg_exito = f"Cita finalizada exitosamente para {cita.paciente.usuario.nombre_completo}. Notas clínicas guardadas."

        # RN-ESP-10: Agendamiento directo de cita de control al finalizar
        if agendar_control and fecha_control_str:
            dt_control = timezone.make_aware(datetime.strptime(f"{fecha_control_str} {hora_control_str}", "%Y-%m-%d %H:%M"))
            agendar_cita_web(
                paciente=cita.paciente,
                especialista=especialista,
                consultorio=especialista.consultorio,
                fecha_hora_inicio=dt_control,
                duracion_minutos=30
            )
            msg_exito += f" Se programó automáticamente la Cita de Control Directo para el {fecha_control_str} a las {hora_control_str}."

        messages.success(request, msg_exito)
    except Exception as e:
        messages.error(request, str(e))

    return redirect('dashboard_especialista')


@login_required(login_url='login')
@require_POST
def especialista_solicitar_permiso_view(request):
    """
    HU04 / RN-ESP-02: Solicitud de Ausencias Programadas (Específica por Día de Ausencia).
    El especialista selecciona el día exacto de la ausencia. La fecha de hoy se registra para auditoría.
    """
    especialista = obtener_perfil_especialista(request.user)
    if not especialista:
        messages.error(request, "Perfil médico no encontrado.")
        return redirect('dashboard_especialista')

    fecha_inicio_str = request.POST.get('fecha_hora_inicio', '').strip()
    fecha_fin_str = request.POST.get('fecha_hora_fin', '').strip()
    motivo = request.POST.get('motivo_solicitud', '').strip()

    if not fecha_inicio_str or not fecha_fin_str or not motivo:
        messages.error(request, "Por favor completa las fechas y el motivo de la solicitud.")
        return redirect('especialista_permisos')

    try:
        dt_inicio_raw = datetime.strptime(fecha_inicio_str, "%Y-%m-%dT%H:%M")
        dt_fin_raw = datetime.strptime(fecha_fin_str, "%Y-%m-%dT%H:%M")

        inicio_dt = timezone.make_aware(dt_inicio_raw)
        fin_dt = timezone.make_aware(dt_fin_raw)

        if fin_dt <= inicio_dt:
            messages.error(request, "La fecha y hora de fin debe ser posterior a la fecha de inicio.")
            return redirect('especialista_permisos')

        # RN-ESP-02: Anticipación Mínima para Solicitud de Ausencias (24 Horas)
        ahora = timezone.now()
        if (inicio_dt - ahora).total_seconds() < 86400:
            messages.error(
                request,
                "RN-ESP-02: Toda solicitud de permiso o ausencia programada debe registrarse con al menos 24 horas de anticipación. "
                "Las inasistencias imprevistas del mismo día deben tramitarse exclusivamente como 'Ausencia de Emergencia' a través de Recepción o Administrador."
            )
            return redirect('especialista_permisos')

        solicitar_permiso_especialista(especialista, inicio_dt, fin_dt, motivo)
        messages.success(
            request,
            f"Solicitud registrada exitosamente desde {inicio_dt.strftime('%d/%m/%Y %I:%M %p')}. Queda en estado Pendiente para aprobación."
        )
    except ValueError:
        messages.error(request, "Formato de fecha u hora inválido. Usa el selector del calendario.")
    except Exception as e:
        messages.error(request, str(e))

    return redirect('especialista_permisos')




@login_required(login_url='login')
def especialista_inicio_view(request):
    """
    Dashboard de Inicio del Especialista Médico.
    Muestra un resumen rápido de su estado y estadísticas de citas.
    """
    if not es_especialista_o_admin(request.user):
        messages.error(request, "Acceso no autorizado al panel del especialista.")
        return redirect('dashboard')

    especialista = obtener_perfil_especialista(request.user)
    if not especialista:
        messages.warning(request, "Tu cuenta no tiene un perfil médico asignado. Contacta al administrador.")
        return redirect('dashboard')

    ahora = timezone.now()
    inicio_dia = timezone.make_aware(datetime.combine(ahora.date(), datetime.min.time()))
    fin_dia = timezone.make_aware(datetime.combine(ahora.date(), datetime.max.time()))

    citas_hoy = Cita.objects.filter(
        especialista=especialista,
        fecha_hora_inicio__gte=inicio_dia,
        fecha_hora_inicio__lte=fin_dia
    )

    cant_total = citas_hoy.count()
    cant_atendidas = citas_hoy.filter(estado_cita=EstadoCita.ATENDIDA).count()
    cant_pendientes = citas_hoy.filter(estado_cita__in=[EstadoCita.PROGRAMADA, EstadoCita.EN_SALA]).count()
    
    proxima_cita = citas_hoy.filter(
        fecha_hora_inicio__gte=ahora,
        estado_cita__in=[EstadoCita.PROGRAMADA, EstadoCita.EN_SALA]
    ).order_by('fecha_hora_inicio').first()

    context = {
        'especialista': especialista,
        'cant_total': cant_total,
        'cant_atendidas': cant_atendidas,
        'cant_pendientes': cant_pendientes,
        'proxima_cita': proxima_cita,
        'fecha_actual': ahora.date()
    }
    return render(request, 'agendamiento/dashboard/especialista_inicio.html', context)


@login_required(login_url='login')
def especialista_agenda_completa_view(request):
    """
    Vista de Agenda Completa (Calendario) para el Especialista.
    """
    if not es_especialista_o_admin(request.user):
        return redirect('dashboard')

    especialista = obtener_perfil_especialista(request.user)
    if not especialista:
        return redirect('dashboard')

    context = {
        'especialista': especialista,
        'EstadoCita': EstadoCita
    }
    return render(request, 'agendamiento/citas/especialista_agenda_completa.html', context)


@login_required(login_url='login')
def especialista_pacientes_view(request):
    """
    Vista para listar de forma cronológica todas las citas atendidas por el especialista
    y ver los historiales clínicos.
    """
    if not es_especialista_o_admin(request.user):
        return redirect('dashboard')

    especialista = obtener_perfil_especialista(request.user)
    if not especialista:
        return redirect('dashboard')

    query = request.GET.get('q', '').strip()
    citas_atendidas = Cita.objects.select_related('paciente__usuario').filter(
        especialista=especialista,
        estado_cita=EstadoCita.ATENDIDA
    ).order_by('-fecha_hora_inicio')

    if query:
        citas_atendidas = citas_atendidas.filter(
            paciente__usuario__nombre_completo__icontains=query
        ) | citas_atendidas.filter(
            paciente__usuario__num_documento__icontains=query
        )

    context = {
        'especialista': especialista,
        'citas': citas_atendidas.distinct(),
        'query': query,
        'EstadoCita': EstadoCita
    }
    return render(request, 'agendamiento/citas/especialista_pacientes.html', context)


@login_required(login_url='login')
def especialista_permisos_view(request):
    """
    Vista dedicada para ver y solicitar permisos del especialista.
    """
    if not es_especialista_o_admin(request.user):
        return redirect('dashboard')

    especialista = obtener_perfil_especialista(request.user)
    if not especialista:
        return redirect('dashboard')

    permisos = AusenciasPermisos.objects.filter(especialista=especialista).order_by('-fecha_hora_inicio')

    context = {
        'especialista': especialista,
        'permisos': permisos,
        'fecha_actual_display': timezone.now(),
        'fecha_seleccionada': timezone.now().strftime('%Y-%m-%d'),
        'EstadoAprobacion': EstadoAprobacion
    }
    return render(request, 'agendamiento/citas/especialista_permisos.html', context)

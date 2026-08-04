from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime

from agendamiento.models.usuarios import RolUsuario
from agendamiento.models.citas import Cita, EstadoCita
from agendamiento.models.pacientes import Paciente
from agendamiento.models.especialistas import Especialista, Consultorio
from agendamiento.services.citas_service import (
    reprogramar_cita,
    cancelar_cita,
    registrar_inasistencia,
    activar_contingencia_emergencia
)


@login_required(login_url='login')
def recepcionista_agendar_view(request):
    """HU06: Agendamiento administrativo sin restricción de 24h."""
    allowed = [RolUsuario.RECEPCIONISTA, RolUsuario.ADMINISTRADOR]
    if request.user.rol not in allowed:
        messages.error(request, "No tienes permiso para realizar esta acción.")
        return redirect('login')

    if request.method == 'POST':
        paciente_id = request.POST.get('paciente_id')
        especialista_id = request.POST.get('especialista_id')
        consultorio_id = request.POST.get('consultorio_id')
        fecha_str = request.POST.get('fecha')
        hora_str = request.POST.get('hora')

        try:
            paciente = get_object_or_404(Paciente, id=paciente_id)
            especialista = get_object_or_404(Especialista, id=especialista_id)
            consultorio = get_object_or_404(Consultorio, id=consultorio_id)

            dt_str = f"{fecha_str} {hora_str}"
            fecha_hora_inicio = timezone.make_aware(datetime.strptime(dt_str, "%Y-%m-%d %H:%M"))
            fecha_hora_fin = fecha_hora_inicio + timezone.timedelta(minutes=30)

            Cita.objects.create(
                paciente=paciente,
                especialista=especialista,
                consultorio=consultorio,
                fecha_hora_inicio=fecha_hora_inicio,
                fecha_hora_fin=fecha_hora_fin,
                estado_cita=EstadoCita.PROGRAMADA
            )
            messages.success(request, "Cita agendada correctamente por Recepción.")
        except Exception as e:
            messages.error(request, f"Error al agendar cita: {e}")

    return redirect('dashboard_recepcionista')


@login_required(login_url='login')
def recepcionista_cambiar_estado_view(request, cita_id):
    """HU06 / HU07: Cambio manual de estado por Recepción (En_Sala, Atendida, No_Asistio, Cancelada)."""
    allowed = [RolUsuario.RECEPCIONISTA, RolUsuario.ADMINISTRADOR]
    if request.user.rol not in allowed:
        return redirect('login')

    cita = get_object_or_404(Cita, id=cita_id)

    if request.method == 'POST':
        nuevo_estado = request.POST.get('nuevo_estado')
        try:
            if nuevo_estado == EstadoCita.NO_ASISTIO:
                registrar_inasistencia(cita)
                messages.warning(
                    request,
                    f"Cita marcada como No Asistió. Inasistencias acumuladas del paciente: {cita.paciente.contador_inasistencias}."
                )
            elif nuevo_estado in [EstadoCita.PROGRAMADA, EstadoCita.EN_SALA, EstadoCita.ATENDIDA, EstadoCita.CANCELADA]:
                cita.estado_cita = nuevo_estado
                cita.save()
                messages.success(request, f"Estado de la cita actualizado a {cita.get_estado_cita_display()}.")
        except Exception as e:
            messages.error(request, f"Error al actualizar estado de la cita: {e}")

    return redirect('dashboard_recepcionista')


@login_required(login_url='login')
def recepcionista_reprogramar_view(request, cita_id):
    """HU06: Reprogramación administrativa ignorando regla de 24h."""
    allowed = [RolUsuario.RECEPCIONISTA, RolUsuario.ADMINISTRADOR]
    if request.user.rol not in allowed:
        return redirect('login')

    cita = get_object_or_404(Cita, id=cita_id)

    if request.method == 'POST':
        nueva_fecha_str = request.POST.get('nueva_fecha')
        nueva_hora_str = request.POST.get('nueva_hora')

        try:
            dt_str = f"{nueva_fecha_str} {nueva_hora_str}"
            nueva_fecha_hora = timezone.make_aware(datetime.strptime(dt_str, "%Y-%m-%d %H:%M"))

            reprogramar_cita(cita=cita, nueva_fecha_hora_inicio=nueva_fecha_hora, es_recepcion=True)
            messages.success(request, "Cita reprogramada exitosamente por Recepción.")
        except ValidationError as ve:
            messages.error(request, str(ve.message if hasattr(ve, 'message') else ve))
        except Exception as e:
            messages.error(request, f"Error al reprogramar: {e}")

    return redirect('dashboard_recepcionista')


@login_required(login_url='login')
def recepcionista_contingencia_emergencia_view(request):
    """HU14 / RN08: Contingencia por ausencia médica de emergencia."""
    allowed = [RolUsuario.RECEPCIONISTA, RolUsuario.ADMINISTRADOR]
    if request.user.rol not in allowed:
        return redirect('login')

    if request.method == 'POST':
        especialista_id = request.POST.get('especialista_id')
        try:
            especialista = get_object_or_404(Especialista, id=especialista_id)
            citas_afectadas = activar_contingencia_emergencia(especialista, request.user)
            messages.warning(
                request,
                f"Contingencia activada para el/la Dr/Dra. {especialista.usuario.nombre_completo}. "
                f"Se han pasado {len(citas_afectadas)} citas a 'Pendiente de Reubicación' y se notificó a los pacientes."
            )
        except Exception as e:
            messages.error(request, f"Error al activar la contingencia: {e}")

    return redirect('dashboard_recepcionista')

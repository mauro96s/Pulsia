from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime

from ..models.usuarios import RolUsuario
from ..models.citas import Cita, EstadoCita, AusenciasPermisos, EstadoAprobacion
from ..models.especialistas import Especialista, EstadoTurno
from ..services.citas_service import registrar_notas_clinicas


@login_required(login_url='login')
def especialista_checkin_view(request):
    """HU13: Check-in médico / inicio de turno."""
    if request.user.rol != RolUsuario.ESPECIALISTA:
        messages.error(request, "Acceso no autorizado.")
        return redirect('login')

    especialista = getattr(request.user, 'perfil_especialista', None)
    if not especialista:
        messages.error(request, "Perfil de especialista no encontrado.")
        return redirect('dashboard_especialista')

    if request.method == 'POST':
        # Alternar estado
        if especialista.estado_turno == EstadoTurno.PRESENTE:
            especialista.estado_turno = EstadoTurno.AUSENTE
            messages.info(request, "Has finalizado tu turno laboral.")
        else:
            especialista.estado_turno = EstadoTurno.PRESENTE
            messages.success(request, "¡Turno iniciado con éxito! Recepción ya puede ver tu disponibilidad.")
        especialista.save()

    return redirect('dashboard_especialista')


@login_required(login_url='login')
def especialista_cambiar_estado_view(request, cita_id):
    """Permite al médico cambiar el estado de una cita a En_Sala o Atendida."""
    if request.user.rol != RolUsuario.ESPECIALISTA:
        return redirect('login')

    especialista = getattr(request.user, 'perfil_especialista', None)
    cita = get_object_or_404(Cita, id=cita_id, especialista=especialista)

    if request.method == 'POST':
        nuevo_estado = request.POST.get('nuevo_estado')
        if nuevo_estado in [EstadoCita.EN_SALA, EstadoCita.ATENDIDA]:
            cita.estado_cita = nuevo_estado
            cita.save()
            messages.success(request, f"La cita ha cambiado a estado {cita.get_estado_cita_display()}.")

    return redirect('dashboard_especialista')


@login_required(login_url='login')
def especialista_guardar_notas_view(request, cita_id):
    """HU05 / RN06: Registra notas clínicas y recomendaciones."""
    if request.user.rol != RolUsuario.ESPECIALISTA:
        return redirect('login')

    especialista = getattr(request.user, 'perfil_especialista', None)
    cita = get_object_or_404(Cita, id=cita_id, especialista=especialista)

    if request.method == 'POST':
        notas = request.POST.get('notas_clinicas', '').strip()
        try:
            registrar_notas_clinicas(cita, request.user, notas)
            messages.success(request, "Notas clínicas registradas correctamente en la historia del paciente.")
        except ValidationError as ve:
            messages.error(request, str(ve.message if hasattr(ve, 'message') else ve))
        except Exception as e:
            messages.error(request, f"Error al guardar notas: {e}")

    return redirect('dashboard_especialista')


@login_required(login_url='login')
def especialista_solicitar_ausencia_view(request):
    """HU04: Solicita bloqueo temporal de agenda (permiso/ausencia)."""
    if request.user.rol != RolUsuario.ESPECIALISTA:
        return redirect('login')

    especialista = getattr(request.user, 'perfil_especialista', None)
    if request.method == 'POST':
        inicio_str = request.POST.get('fecha_inicio')
        fin_str = request.POST.get('fecha_fin')
        motivo = request.POST.get('motivo', '').strip()

        try:
            dt_inicio = timezone.make_aware(datetime.strptime(inicio_str, "%Y-%m-%dT%H:%M"))
            dt_fin = timezone.make_aware(datetime.strptime(fin_str, "%Y-%m-%dT%H:%M"))

            if dt_fin <= dt_inicio:
                messages.error(request, "La fecha de fin debe ser posterior a la fecha de inicio.")
            else:
                AusenciasPermisos.objects.create(
                    especialista=especialista,
                    fecha_hora_inicio=dt_inicio,
                    fecha_hora_fin=dt_fin,
                    motivo_solicitud=motivo,
                    estado_aprobacion=EstadoAprobacion.PENDIENTE
                )
                messages.success(request, "Solicitud de ausencia registrada con éxito. Pendiente de aprobación por administración.")
        except Exception as e:
            messages.error(request, f"Error al procesar la solicitud de ausencia: {e}")

    return redirect('dashboard_especialista')

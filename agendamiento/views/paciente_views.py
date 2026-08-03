from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime, time

from ..models.usuarios import RolUsuario
from ..models.citas import Cita, EstadoCita, ListaEspera
from ..models.especialistas import Especialidad, Especialista, Consultorio, HorarioLaboral
from ..services.citas_service import (
    agendar_cita_web,
    reprogramar_cita,
    cancelar_cita,
    unirse_lista_espera
)


@login_required(login_url='login')
def paciente_agendar_view(request):
    """Acción y vista de agendamiento web autónomo del paciente estilo cine (HU02)."""
    if request.user.rol != RolUsuario.PACIENTE:
        messages.error(request, "Acceso no autorizado.")
        return redirect('login')

    paciente = getattr(request.user, 'perfil_paciente', None)
    if not paciente:
        messages.error(request, "No se encontró el perfil del paciente.")
        return redirect('dashboard_paciente')

    if request.method == 'POST':
        especialista_id = request.POST.get('especialista_id')
        fecha_str = request.POST.get('fecha')
        hora_str = request.POST.get('hora')
        acepta_habeas = request.POST.get('acepta_habeas_data') == 'on'

        if not acepta_habeas:
            messages.error(request, "Debes aceptar la política de tratamiento de datos (Habeas Data).")
            return redirect('paciente_agendar')

        try:
            especialista = get_object_or_404(Especialista, id=especialista_id)
            # Consultorio por defecto asignado o primero disponible
            consultorio = Consultorio.objects.filter(estado_operativo=True).first()
            if not consultorio:
                messages.error(request, "No hay consultorios disponibles en el sistema.")
                return redirect('paciente_agendar')

            dt_str = f"{fecha_str} {hora_str}"
            fecha_hora = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
            fecha_hora = timezone.make_aware(fecha_hora)

            agendar_cita_web(
                paciente=paciente,
                especialista=especialista,
                consultorio=consultorio,
                fecha_hora_inicio=fecha_hora
            )
            messages.success(request, "¡Tu cita médica ha sido agendada con éxito!")
            return redirect('dashboard_paciente')
        except ValidationError as ve:
            messages.error(request, str(ve.message if hasattr(ve, 'message') else ve))
            return redirect('paciente_agendar')
        except Exception as e:
            messages.error(request, f"Error al procesar el agendamiento: {e}")
            return redirect('paciente_agendar')

    especialistas_frecuentes = Especialista.objects.filter(
        citas__paciente=paciente
    ).select_related('usuario', 'especialidad').distinct()

    context = {
        'especialidades': Especialidad.objects.all(),
        'especialistas': Especialista.objects.select_related('usuario', 'especialidad').all(),
        'especialistas_frecuentes': especialistas_frecuentes,
        'es_paciente_frecuente': especialistas_frecuentes.exists(),
    }
    return render(request, 'agendamiento/citas/agendar.html', context)


@login_required(login_url='login')
def paciente_reprogramar_view(request, cita_id):
    """Reprogramación web por el paciente (HU03, RN01, RN02)."""
    if request.user.rol != RolUsuario.PACIENTE:
        return redirect('login')

    paciente = getattr(request.user, 'perfil_paciente', None)
    cita = get_object_or_404(Cita, id=cita_id, paciente=paciente)

    if request.method == 'POST':
        nueva_fecha_str = request.POST.get('nueva_fecha')
        nueva_hora_str = request.POST.get('nueva_hora')

        try:
            dt_str = f"{nueva_fecha_str} {nueva_hora_str}"
            nueva_fecha_hora = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
            nueva_fecha_hora = timezone.make_aware(nueva_fecha_hora)

            reprogramar_cita(
                cita=cita,
                nueva_fecha_hora_inicio=nueva_fecha_hora,
                es_recepcion=False
            )
            messages.success(request, "Tu cita ha sido reprogramada exitosamente.")
        except ValidationError as ve:
            messages.error(request, str(ve.message if hasattr(ve, 'message') else ve))
        except Exception as e:
            messages.error(request, f"Ocurrió un error al reprogramar: {e}")

    return redirect('dashboard_paciente')


@login_required(login_url='login')
def paciente_cancelar_view(request, cita_id):
    """Cancelación web por el paciente (RN02)."""
    if request.user.rol != RolUsuario.PACIENTE:
        return redirect('login')

    paciente = getattr(request.user, 'perfil_paciente', None)
    cita = get_object_or_404(Cita, id=cita_id, paciente=paciente)

    if request.method == 'POST':
        try:
            cancelar_cita(cita=cita, es_recepcion=False)
            messages.success(request, "Tu cita ha sido cancelada.")
        except ValidationError as ve:
            messages.error(request, str(ve.message if hasattr(ve, 'message') else ve))
        except Exception as e:
            messages.error(request, f"Error al cancelar la cita: {e}")

    return redirect('dashboard_paciente')


@login_required(login_url='login')
def paciente_unirse_espera_view(request):
    """Inscripción en lista de espera (HU09)."""
    if request.user.rol != RolUsuario.PACIENTE:
        return redirect('login')

    paciente = getattr(request.user, 'perfil_paciente', None)
    if request.method == 'POST':
        especialidad_id = request.POST.get('especialidad_id')
        especialista_id = request.POST.get('especialista_id')

        try:
            especialidad = Especialidad.objects.filter(id=especialidad_id).first() if especialidad_id else None
            especialista = Especialista.objects.filter(id=especialista_id).first() if especialista_id else None

            unirse_lista_espera(
                paciente=paciente,
                especialista=especialista,
                especialidad=especialidad
            )
            messages.success(request, "Te has inscrito exitosamente en la lista de espera.")
        except ValidationError as ve:
            messages.error(request, str(ve.message if hasattr(ve, 'message') else ve))
        except Exception as e:
            messages.error(request, f"Error al inscribirse en lista de espera: {e}")

    return redirect('dashboard_paciente')

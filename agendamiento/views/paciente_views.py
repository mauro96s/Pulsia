from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime, time

from agendamiento.models.usuarios import RolUsuario
from agendamiento.models.citas import Cita, EstadoCita, ListaEspera
from agendamiento.models.especialistas import Especialidad, Especialista, Consultorio, HorarioLaboral
from agendamiento.services.citas_service import (
    agendar_cita_web,
    reprogramar_cita,
    cancelar_cita,
    unirse_lista_espera
)
from agendamiento.views.dashboard_views import _generar_eventos_fullcalendar


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
        especialidad_id = request.POST.get('especialidad_id')
        fecha_str = request.POST.get('fecha')
        hora_str = request.POST.get('hora')
        acepta_habeas_data = request.POST.get('acepta_habeas_data') == 'on'

        try:
            fecha_dt = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            hora_dt = datetime.strptime(hora_str, '%H:%M').time()
            fecha_hora_inicio = timezone.make_aware(datetime.combine(fecha_dt, hora_dt))

            if especialista_id:
                especialista = get_object_or_404(Especialista, id=especialista_id)
            else:
                # Auto-asignar médico disponible para la especialidad y hora elegida
                dia_semana = fecha_dt.isoweekday()
                candidatos = Especialista.objects.all()
                if especialidad_id:
                    candidatos = candidatos.filter(especialidad_id=especialidad_id)

                especialista_asignado = None
                for cand in candidatos:
                    horario = HorarioLaboral.objects.filter(especialista=cand, dia_semana=dia_semana).first()
                    if not horario:
                        continue
                    if not (horario.hora_inicio <= hora_dt < horario.hora_fin):
                        continue
                    if horario.hora_inicio_descanso and horario.hora_fin_descanso:
                        if horario.hora_inicio_descanso <= hora_dt < horario.hora_fin_descanso:
                            continue

                    ocupado = Cita.objects.filter(
                        especialista=cand,
                        fecha_hora_inicio=fecha_hora_inicio,
                        estado_cita__in=['Programada', 'En_Sala']
                    ).exists()

                    if not ocupado:
                        especialista_asignado = cand
                        break

                if not especialista_asignado:
                    raise ValidationError(f"No hay ningún médico especialista disponible a las {hora_str}.")
                especialista = especialista_asignado

            consultorio = especialista.consultorio_asignado
            if not consultorio:
                consultorio = Consultorio.objects.filter(estado_operativo=True).first()
                if not consultorio:
                    raise ValidationError("No hay consultorios operativos disponibles.")

            agendar_cita_web(
                paciente=paciente,
                especialista=especialista,
                consultorio=consultorio,
                fecha_hora_inicio=fecha_hora_inicio
            )
            messages.success(request, f"¡Tu cita médica ha sido agendada con éxito con {especialista.usuario.nombre_completo}!")
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

    import json
    citas_ocupadas = Cita.objects.select_related('paciente__usuario', 'especialista__usuario', 'especialista__especialidad', 'consultorio').all()
    horarios_data = {}
    for h in HorarioLaboral.objects.select_related('especialista__usuario', 'especialista__especialidad', 'especialista__consultorio_asignado').all():
        s_id = str(h.especialista_id)
        esp_id = str(h.especialista.especialidad_id)
        if s_id not in horarios_data:
            horarios_data[s_id] = {
                'especialidad_id': esp_id,
                'nombre_medico': h.especialista.usuario.nombre_completo,
                'consultorio': h.especialista.consultorio_asignado.nombre_codigo if h.especialista.consultorio_asignado else 'Sin Asignar',
                'horarios': {}
            }
        horarios_data[s_id]['horarios'][str(h.dia_semana)] = {
            'inicio': h.hora_inicio.strftime('%H:%M'),
            'fin': h.hora_fin.strftime('%H:%M'),
            'desc_inicio': h.hora_inicio_descanso.strftime('%H:%M') if h.hora_inicio_descanso else None,
            'desc_fin': h.hora_fin_descanso.strftime('%H:%M') if h.hora_fin_descanso else None,
        }

    context = {
        'especialidades': Especialidad.objects.all(),
        'especialistas': Especialista.objects.select_related('usuario', 'especialidad').all(),
        'especialistas_frecuentes': especialistas_frecuentes,
        'es_paciente_frecuente': especialistas_frecuentes.exists(),
        'fullcalendar_events_json': _generar_eventos_fullcalendar(citas_ocupadas),
        'horarios_especialistas_json': json.dumps(horarios_data),
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

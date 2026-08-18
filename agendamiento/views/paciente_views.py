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
    agendar_cita_recepcion_balanceada,
    reprogramar_cita,
    cancelar_cita,
    unirse_lista_espera
)
from agendamiento.views.dashboard_views import _generar_eventos_fullcalendar


@login_required(login_url='login')
def paciente_inicio_view(request):
    """
    Dashboard de Inicio del Paciente (equivalente a especialista_inicio).
    Muestra indicadores principales, próxima cita destacada y accesos rápidos.
    """
    if request.user.rol != RolUsuario.PACIENTE:
        messages.error(request, "Acceso no autorizado.")
        return redirect('login')

    paciente = getattr(request.user, 'perfil_paciente', None)
    if not paciente:
        messages.error(request, "No se encontró el perfil del paciente.")
        return redirect('login')

    ahora = timezone.now()

    # 1. Citas Próximas Activas
    citas_activas = Cita.objects.select_related(
        'especialista__usuario', 'especialista__especialidad', 'consultorio'
    ).filter(
        paciente=paciente,
        estado_cita__in=[EstadoCita.PROGRAMADA, EstadoCita.EN_SALA, EstadoCita.PENDIENTE_REUBICACION]
    ).order_by('fecha_hora_inicio')

    # 2. Citas Atendidas
    cant_atendidas = Cita.objects.filter(
        paciente=paciente,
        estado_cita=EstadoCita.ATENDIDA
    ).count()

    # 3. Lista de Espera Activas
    cant_espera = ListaEspera.objects.filter(paciente=paciente).count()

    # 4. Próxima Cita Médica Destacada
    proxima_cita = citas_activas.first()

    inasistencias = getattr(paciente, 'inasistencias_acumuladas', 0)
    bloqueado = getattr(paciente, 'bloqueado_agendamiento_web', False) or (inasistencias >= 3)

    context = {
        'paciente': paciente,
        'cant_activas': citas_activas.count(),
        'cant_atendidas': cant_atendidas,
        'cant_espera': cant_espera,
        'inasistencias_acumuladas': inasistencias,
        'bloqueado_agendamiento_web': bloqueado,
        'proxima_cita': proxima_cita,
        'fecha_actual': ahora.date()
    }
    return render(request, 'agendamiento/dashboard/paciente_inicio.html', context)


@login_required(login_url='login')
def paciente_agenda_view(request):
    """
    Vista de Agenda Completa en Calendario para el Paciente.
    Muestra calendario mensual/semanal de citas, barra de filtros y modal para reagendar.
    """
    if request.user.rol != RolUsuario.PACIENTE:
        return redirect('login')

    paciente = getattr(request.user, 'perfil_paciente', None)
    if not paciente:
        return redirect('login')

    especialidades = Especialidad.objects.all()
    especialistas = Especialista.objects.select_related('usuario', 'especialidad').filter(usuario__estado_cuenta=True)

    inasistencias = getattr(paciente, 'contador_inasistencias', 0)
    bloqueado = getattr(paciente, 'bloqueado_agendamiento_web', False) or (inasistencias >= 3)

    context = {
        'paciente': paciente,
        'especialidades': especialidades,
        'especialistas': especialistas,
        'bloqueado_agendamiento_web': bloqueado,
        'EstadoCita': EstadoCita
    }
    return render(request, 'agendamiento/citas/paciente_agenda.html', context)


@login_required(login_url='login')
def paciente_historial_view(request):
    """
    Vista de Historial Clínico y Citas Atendidas del Paciente.
    Tabla de historial médico y consultas con buscador en tiempo real.
    """
    if request.user.rol != RolUsuario.PACIENTE:
        return redirect('login')

    paciente = getattr(request.user, 'perfil_paciente', None)
    if not paciente:
        return redirect('login')

    query = request.GET.get('q', '').strip()
    estado_filtro = request.GET.get('estado', '').strip()

    citas_qs = Cita.objects.select_related(
        'especialista__usuario', 'especialista__especialidad', 'consultorio'
    ).filter(paciente=paciente).order_by('-fecha_hora_inicio')

    if query:
        citas_qs = citas_qs.filter(
            especialista__usuario__nombre_completo__icontains=query
        ) | citas_qs.filter(
            especialista__especialidad__nombre_especialidad__icontains=query
        )

    if estado_filtro:
        citas_qs = citas_qs.filter(estado_cita=estado_filtro)

    citas_atendidas = citas_qs.filter(estado_cita=EstadoCita.ATENDIDA)

    context = {
        'paciente': paciente,
        'citas_todas': citas_qs,
        'citas_atendidas': citas_atendidas,
        'query': query,
        'estado_filtro': estado_filtro,
        'EstadoCita': EstadoCita
    }
    return render(request, 'agendamiento/citas/paciente_historial.html', context)


@login_required(login_url='login')
def paciente_agendar_view(request):
    """Acción y vista de agendamiento web autónomo del paciente (HU02 / Reagendamiento)."""
    if request.user.rol != RolUsuario.PACIENTE:
        messages.error(request, "Acceso no autorizado.")
        return redirect('login')

    paciente = getattr(request.user, 'perfil_paciente', None)
    if not paciente:
        messages.error(request, "No se encontró el perfil del paciente.")
        return redirect('dashboard_paciente')

    if request.method == 'POST':
        reagendar_cita_id = request.POST.get('reagendar_cita_id')
        especialista_id = request.POST.get('especialista_id')
        especialidad_id = request.POST.get('especialidad_id')
        fecha_str = request.POST.get('fecha')
        hora_str = request.POST.get('hora')
        acepta_habeas_data = request.POST.get('acepta_habeas_data') == 'on'

        # Si se trata de un reagendamiento de cita existente
        if reagendar_cita_id:
            cita_existente = get_object_or_404(Cita, id=reagendar_cita_id, paciente=paciente)
            try:
                dt_str = f"{fecha_str} {hora_str}"
                nueva_fecha_hora = timezone.make_aware(datetime.strptime(dt_str, "%Y-%m-%d %H:%M"))
                reprogramar_cita(cita=cita_existente, nueva_fecha_hora_inicio=nueva_fecha_hora, es_recepcion=False)
                messages.success(request, f"¡Tu cita con Dr/Dra. {cita_existente.especialista.usuario.nombre_completo} ha sido reprogramada exitosamente!")
                return redirect('paciente_agenda')
            except (ValidationError, ValueError) as ve:
                msg = str(ve.message if hasattr(ve, 'message') else ve)
                messages.error(request, msg)
                return redirect(f"{request.path}?cita_id={reagendar_cita_id}")
            except Exception as e:
                messages.error(request, f"Error al reprogramar la cita: {e}")
                return redirect(f"{request.path}?cita_id={reagendar_cita_id}")

        try:
            fecha_dt = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            hora_dt = datetime.strptime(hora_str, '%H:%M').time()
            fecha_hora_inicio = timezone.make_aware(datetime.combine(fecha_dt, hora_dt))

            especialidad = Especialidad.objects.filter(id=especialidad_id).first() if especialidad_id else None

            # Si no selecciona especialista (o deja "-- Cualquier Médico Disponible --"), 
            # se asigna automáticamente un médico con agenda libre de esa especialidad.
            cita_creada = agendar_cita_recepcion_balanceada(
                paciente=paciente,
                especialidad=especialidad,
                especialista_id=especialista_id if especialista_id else None,
                fecha_hora_inicio=fecha_hora_inicio,
                duracion_minutos=30
            )

            messages.success(
                request,
                f"¡Tu cita de {cita_creada.especialista.especialidad.nombre_especialidad} ha sido agendada con éxito con Dr/Dra. {cita_creada.especialista.usuario.nombre_completo} (Consultorio {cita_creada.consultorio.nombre_codigo})!"
            )
            return redirect('paciente_agenda')
        except (ValidationError, ValueError) as ve:
            msg = str(ve.message if hasattr(ve, 'message') else ve)
            messages.error(request, msg)
            return redirect('paciente_agendar')
        except Exception as e:
            messages.error(request, f"Error al procesar el agendamiento: {e}")
            return redirect('paciente_agendar')

    # Manejo de precarga de Cita a Reagendar en GET
    cita_id = request.GET.get('cita_id') or request.GET.get('reagendar_id')
    cita_reagendar = None
    if cita_id:
        cita_reagendar = Cita.objects.filter(id=cita_id, paciente=paciente).select_related(
            'especialista__usuario', 'especialista__especialidad', 'consultorio'
        ).first()

    especialistas_frecuentes = Especialista.objects.filter(
        citas__paciente=paciente
    ).select_related('usuario', 'especialidad').distinct()

    import json
    citas_ocupadas = Cita.objects.select_related('paciente__usuario', 'especialista__usuario', 'especialista__especialidad', 'consultorio').all()
    horarios_data = {}
    for h in HorarioLaboral.objects.select_related('especialista__usuario', 'especialista__especialidad', 'especialista__consultorio', 'especialista__consultorio_asignado').all():
        s_id = str(h.especialista_id)
        esp_id = str(h.especialista.especialidad_id)
        c_obj = h.especialista.consultorio or h.especialista.consultorio_asignado
        consultorio_nombre = c_obj.nombre_codigo if c_obj else 'Sin Asignar'
        if s_id not in horarios_data:
            horarios_data[s_id] = {
                'especialidad_id': esp_id,
                'nombre_medico': h.especialista.usuario.nombre_completo,
                'consultorio': consultorio_nombre,
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
        'cita_reagendar': cita_reagendar,
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

    return redirect('paciente_agenda')


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


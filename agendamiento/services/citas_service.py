"""
Capa de Servicios para la lógica del agendamiento y validación estricta de Reglas de Negocio (RN01 - RN08).
"""
import datetime
from django.utils import timezone
from django.core.exceptions import ValidationError

from agendamiento.models.citas import Cita, EstadoCita, AusenciasPermisos, EstadoAprobacion, ListaEspera, EstadoListaEspera
from agendamiento.models.pacientes import Paciente
from agendamiento.models.especialistas import Especialista, EstadoTurno, HorarioLaboral, Consultorio
from agendamiento.services.festivos_service import es_dia_festivo
from agendamiento.services.notificaciones_service import (
    notificar_confirmacion_cita,
    notificar_reprogramacion_cita,
    notificar_cancelacion_institucional,
    notificar_lista_espera_liberacion
)


def agendar_cita_web(paciente, especialista, consultorio, fecha_hora_inicio, duracion_minutos=30):
    """
    Agendamiento autónomo desde el portal del paciente (HU02).
    Aplica RN04 (bloqueo por inasistencias), validación de festivos y horarios de descanso (HU08).
    """
    # RN04: Verificar si el paciente está penalizado
    if paciente.contador_inasistencias >= 3:
        raise ValidationError(
            "Tu permiso de agendamiento web está bloqueado debido a 3 inasistencias acumuladas (RN04). "
            "Por favor comunícate directamente con recepción o visita la clínica."
        )

    # HU08: Validar festivos
    if es_dia_festivo(fecha_hora_inicio.date()):
        raise ValidationError("No es posible agendar en días festivos nacionales.")

    # Validar que la fecha sea futura
    if fecha_hora_inicio <= timezone.now():
        raise ValidationError("La fecha y hora seleccionada debe ser posterior al momento actual.")

    fecha_hora_fin = fecha_hora_inicio + datetime.timedelta(minutes=duracion_minutos)

    # Validar horario laboral y franja de descanso (HU08)
    dia_semana = fecha_hora_inicio.isoweekday()  # 1: Lunes, 7: Domingo
    horario = HorarioLaboral.objects.filter(especialista=especialista, dia_semana=dia_semana).first()
    if horario:
        hora_c = fecha_hora_inicio.time()
        if hora_c < horario.hora_inicio or hora_c >= horario.hora_fin:
            raise ValidationError("El especialista no atiende en ese horario laboral.")
        if horario.hora_inicio_descanso and horario.hora_fin_descanso:
            if horario.hora_inicio_descanso <= hora_c < horario.hora_fin_descanso:
                raise ValidationError("La hora seleccionada coincide con la franja de descanso del especialista.")

    # Validar ausencias/permisos del especialista
    ausencia = AusenciasPermisos.objects.filter(
        especialista=especialista,
        estado_aprobacion=EstadoAprobacion.APROBADO,
        fecha_hora_inicio__lt=fecha_hora_fin,
        fecha_hora_fin__gt=fecha_hora_inicio
    ).first()
    if ausencia:
        raise ValidationError("El especialista tiene una ausencia o permiso aprobado en ese horario.")

    # Validar traslape de citas del especialista
    traslape_medico = Cita.objects.filter(
        especialista=especialista,
        estado_cita__in=[EstadoCita.PROGRAMADA, EstadoCita.EN_SALA],
        fecha_hora_inicio__lt=fecha_hora_fin,
        fecha_hora_fin__gt=fecha_hora_inicio
    ).exists()
    if traslape_medico:
        raise ValidationError("El especialista ya cuenta con una cita en ese horario.")

    # Validar disponibilidad del consultorio
    traslape_consultorio = Cita.objects.filter(
        consultorio=consultorio,
        estado_cita__in=[EstadoCita.PROGRAMADA, EstadoCita.EN_SALA],
        fecha_hora_inicio__lt=fecha_hora_fin,
        fecha_hora_fin__gt=fecha_hora_inicio
    ).exists()
    if traslape_consultorio:
        raise ValidationError("El consultorio seleccionado ya está ocupado en esta franja horaria.")

    cita = Cita.objects.create(
        paciente=paciente,
        especialista=especialista,
        consultorio=consultorio,
        fecha_hora_inicio=fecha_hora_inicio,
        fecha_hora_fin=fecha_hora_fin,
        estado_cita=EstadoCita.PROGRAMADA
    )

    notificar_confirmacion_cita(cita)
    return cita


def reprogramar_cita(cita, nueva_fecha_hora_inicio, es_recepcion=False, duracion_minutos=30):
    """
    Reprogramación de citas (HU03, HU06).
    Si es_recepcion=False, valida RN01 (máx 1 vez) y RN02 (al menos 24 horas antes).
    """
    ahora = timezone.now()

    if not es_recepcion:
        # RN01: Límite de 1 reprogramación web
        if cita.contador_reprogramacion >= 1:
            raise ValidationError("Ya has alcanzado el límite de 1 reprogramación permitida desde la web (RN01).")

        # RN02: Faltan menos de 24 horas para la cita actual
        diferencia_horas = (cita.fecha_hora_inicio - ahora).total_seconds() / 3600.0
        if diferencia_horas < 24.0:
            raise ValidationError("No es posible reprogramar citas si faltan menos de 24 horas.")

    nueva_fecha_hora_fin = nueva_fecha_hora_inicio + datetime.timedelta(minutes=duracion_minutos)

    # Validar disponibilidad para la nueva fecha
    traslape = Cita.objects.filter(
        especialista=cita.especialista,
        estado_cita__in=[EstadoCita.PROGRAMADA, EstadoCita.EN_SALA],
        fecha_hora_inicio__lt=nueva_fecha_hora_fin,
        fecha_hora_fin__gt=nueva_fecha_hora_inicio
    ).exclude(id=cita.id).exists()

    if traslape:
        raise ValidationError("El especialista ya tiene agendada otra cita en ese nuevo horario.")

    # Guardar nueva fecha
    fecha_anterior = cita.fecha_hora_inicio
    cita.fecha_hora_inicio = nueva_fecha_hora_inicio
    cita.fecha_hora_fin = nueva_fecha_hora_fin
    if not es_recepcion:
        cita.contador_reprogramacion += 1
    cita.estado_cita = EstadoCita.PROGRAMADA
    cita.save()

    # Notificar lista de espera sobre la liberación del horario anterior
    _notificar_espera_tras_liberacion(cita.especialista, fecha_anterior)
    notificar_reprogramacion_cita(cita)
    return cita


def cancelar_cita(cita, es_recepcion=False, es_contingencia=False):
    """
    Cancelación de citas. Si la realiza el paciente, aplica RN02 (anticipación 24h).
    """
    ahora = timezone.now()
    if not es_recepcion and not es_contingencia:
        diferencia_horas = (cita.fecha_hora_inicio - ahora).total_seconds() / 3600.0
        if diferencia_horas < 24.0:
            raise ValidationError("No puedes cancelar tu cita si faltan menos de 24 horas.")

    cita.estado_cita = EstadoCita.CANCELADA
    cita.save()
    
    # RN08: Enviar notificación institucional si es contingencia
    if es_contingencia:
        notificar_cancelacion_institucional(cita)

    # Notificar a lista de espera
    _notificar_espera_tras_liberacion(cita.especialista, cita.fecha_hora_inicio)
    return cita


def registrar_inasistencia(cita):
    """
    Registra el estado No_Asistio en una cita (HU07, RN03, RN04).
    Incremente contador de inasistencias del paciente y bloquea agendamiento web si alcanza 3.
    """
    cita.estado_cita = EstadoCita.NO_ASISTIO
    cita.save()

    paciente = cita.paciente
    paciente.contador_inasistencias += 1
    paciente.save()

    return cita


def registrar_notas_clinicas(cita, especialista_user, notas):
    """
    Registra notas clínicas y recomendaciones (HU05, RN06).
    Exige que la cita esté Atendida y pertenezca al especialista.
    """
    if cita.especialista.usuario != especialista_user:
        raise ValidationError("No tienes autorización para modificar la historia clínica de esta cita.")

    if cita.estado_cita != EstadoCita.ATENDIDA:
        raise ValidationError("Solo se pueden agregar notas clínicas cuando la cita está en estado 'Atendida'.")

    cita.notas_clinicas = notas
    cita.save()
    return cita


def activar_contingencia_emergencia(especialista, recepcionista_user):
    """
    HU14 / RN08: Contingencia por ausencia de emergencia del especialista hoy.
    Cambia estado del médico a Ausente, pasa citas de hoy a Pendiente_Reubicacion y dispara avisos institucionales.
    """
    hoy = timezone.now().date()
    especialista.estado_turno = EstadoTurno.AUSENTE
    especialista.save()

    citas_hoy = Cita.objects.filter(
        especialista=especialista,
        fecha_hora_inicio__date=hoy,
        estado_cita__in=[EstadoCita.PROGRAMADA, EstadoCita.EN_SALA]
    )

    citas_afectadas = []
    for cita in citas_hoy:
        cita.estado_cita = EstadoCita.PENDIENTE_REUBICACION
        cita.save()

        # RN08: Notificación institucional sin consumir reprogramación
        notificar_cancelacion_institucional(cita, motivo="Ausencia de emergencia del especialista")
        citas_afectadas.append(cita)

    return citas_afectadas


def unirse_lista_espera(paciente, especialista=None, especialidad=None, fecha_solicitada=None):
    """Permite al paciente inscribirse en la lista de espera (HU09)."""
    if paciente.contador_inasistencias >= 3:
        raise ValidationError("Tu cuenta está penalizada. No puedes inscribirte en lista de espera (RN04).")

    espera = ListaEspera.objects.create(
        paciente=paciente,
        especialista=especialista,
        especialidad=especialidad,
        fecha_solicitada=fecha_solicitada,
        estado=EstadoListaEspera.PENDIENTE
    )
    return espera


def _notificar_espera_tras_liberacion(especialista, fecha_hora):
    """Notifica al primer paciente en lista de espera cuando se libera una cita."""
    espera = ListaEspera.objects.filter(
        especialista=especialista,
        estado=EstadoListaEspera.PENDIENTE
    ).order_by('fecha_registro').first()

    if espera:
        espera.estado = EstadoListaEspera.NOTIFICADO
        espera.save()
        notificar_lista_espera_liberacion(espera.paciente, especialista, fecha_hora)

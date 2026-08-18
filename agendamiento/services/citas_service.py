"""
Capa de Servicios para la lógica del agendamiento, tolerancia de 10 min, check-in médico, balanceo de carga y desempate aleatorio.
"""

import random
from datetime import datetime, date, time, timedelta
from django.utils import timezone
from django.db import transaction
from django.db.models import Count, Q
from agendamiento.models import (
    Cita, EstadoCita, Paciente, CustomUser, RolUsuario, TipoDocumento,
    Especialista, Consultorio, EstadoTurno, Especialidad
)

def evaluar_tolerancia_cita(cita: Cita, hora_referencia: datetime = None) -> dict:
    """
    Evalúa si la cita está a tiempo, en tolerancia (<= 10 minutos de retraso)
    o si excedió la tolerancia máxima permitida (> 10 minutos).
    """
    if hora_referencia is None:
        hora_referencia = timezone.now()

    if cita.estado_cita != EstadoCita.PROGRAMADA:
        return {
            'estado': 'procesada',
            'mensaje': cita.get_estado_cita_display(),
            'minutos_diferencia': 0,
            'excedido': False
        }

    inicio_cita = cita.fecha_hora_inicio
    if timezone.is_naive(inicio_cita):
        inicio_cita = timezone.make_aware(inicio_cita)

    diferencia = (hora_referencia - inicio_cita).total_seconds() / 60.0

    if diferencia < 0:
        min_restantes = abs(int(diferencia))
        return {
            'estado': 'a_tiempo',
            'mensaje': f'Inicia en {min_restantes} min',
            'minutos_diferencia': int(diferencia),
            'excedido': False
        }
    elif diferencia <= 10:
        min_retraso = int(diferencia)
        return {
            'estado': 'en_tolerancia',
            'mensaje': f'{min_retraso} min de margen (Máx 10 min)',
            'minutos_diferencia': min_retraso,
            'excedido': False
        }
    else:
        min_exceso = int(diferencia)
        return {
            'estado': 'fuera_tolerancia',
            'mensaje': f'{min_exceso} min de retraso (> 10 min)',
            'minutos_diferencia': min_exceso,
            'excedido': True
        }


@transaction.atomic
def marcar_checkin_medico(especialista_id: int, nuevo_estado: str = None) -> Especialista:
    """
    Permite a la recepcionista registrar o conmutar manualmente la asistencia (check-in) de un médico.
    """
    especialista = Especialista.objects.select_related('usuario', 'especialidad', 'consultorio').get(id=especialista_id)
    if nuevo_estado:
        especialista.estado_turno = nuevo_estado
    else:
        especialista.estado_turno = (
            EstadoTurno.PRESENTE if especialista.estado_turno == EstadoTurno.AUSENTE else EstadoTurno.AUSENTE
        )
    especialista.save()
    return especialista


@transaction.atomic
def marcar_llegada_paciente(cita_id: int) -> tuple[Cita, bool, str]:
    """
    Registra el anuncio de llegada del paciente a recepción.
    - Si el médico asignado está PRESENTE: pasa la cita a 'EN_SALA'.
    - Si el médico asignado está AUSENTE / SIN CHECK-IN:
      Ejecuta Auto-Reubicación Inteligente en tiempo real. Si encuentra a otro especialista presente hoy,
      reasigna la cita de inmediato y pasa al paciente a 'EN_SALA' con el nuevo médico notificando por correo.
    """
    cita = Cita.objects.select_related(
        'paciente__usuario', 'especialista__usuario', 'especialista__especialidad'
    ).get(id=cita_id)
    medico = cita.especialista

    if medico.estado_turno == EstadoTurno.PRESENTE:
        cita.estado_cita = EstadoCita.EN_SALA
        cita.save()
        return cita, False, f"Llegada confirmada: {cita.paciente.usuario.nombre_completo} ha ingresado a Sala de Espera con Dr/Dra. {medico.usuario.nombre_completo}."
    else:
        cita.estado_cita = EstadoCita.PENDIENTE_REUBICACION
        cita.save()
        
        from agendamiento.services.ausencias_service import auto_reubicar_cita_inteligente
        exito, cita_nueva, msg_reub = auto_reubicar_cita_inteligente(cita.id, priorizar_mismo_dia=True)
        
        if exito:
            return cita_nueva, False, f"El médico original no asistió. {msg_reub} Se envió correo de notificación al paciente."
        else:
            msg = (
                f"El médico Dr/Dra. {medico.usuario.nombre_completo} no ha registrado asistencia (Sin Check-in). "
                f"La cita quedó registrada en la Bandeja de Reubicación. ({msg_reub})"
            )
            return cita, True, msg



@transaction.atomic
def registrar_inasistencia(cita_id: int) -> tuple[Cita, bool]:
    """
    Marca la cita como 'No_Asistio' (RN03/RN04) por superación del límite de 10 minutos de tolerancia.
    Incrementa el contador de inasistencias del paciente.
    Si alcanza 3 inasistencias, desactiva la cuenta del paciente.
    """
    cita = Cita.objects.select_related('paciente__usuario').get(id=cita_id)
    cita.estado_cita = EstadoCita.NO_ASISTIO
    cita.save()

    paciente = cita.paciente
    paciente.contador_inasistencias += 1
    cuenta_bloqueada = False

    if paciente.contador_inasistencias >= 3:
        paciente.usuario.estado_cuenta = False
        paciente.usuario.save()
        cuenta_bloqueada = True

    paciente.save()
    return cita, cuenta_bloqueada


@transaction.atomic
def crear_paciente_expres(
    nombre_completo: str,
    tipo_documento: str,
    num_documento: str,
    correo: str,
    telefono: str = "",
    fecha_nacimiento: date = None
) -> Paciente:
    """
    Crea un nuevo usuario con rol Paciente y su perfil correspondiente desde Recepción.
    """
    if not fecha_nacimiento:
        fecha_nacimiento = date(1990, 1, 1)

    username = f"paciente_{num_documento}" if num_documento else correo

    user = CustomUser.objects.create_user(
        username=username,
        correo=correo,
        nombre_completo=nombre_completo,
        tipo_documento=tipo_documento,
        num_documento=num_documento,
        telefono=telefono,
        rol=RolUsuario.PACIENTE,
        password=num_documento or "Pulsia2026*"
    )

    paciente = Paciente.objects.create(
        usuario=user,
        fecha_nacimiento=fecha_nacimiento,
        acepta_habeas_data=True
    )
    return paciente


@transaction.atomic
def agendar_cita_recepcion_balanceada(
    paciente_id=None,
    especialidad_id=None,
    fecha_hora_inicio: datetime = None,
    especialista_id=None,
    duracion_minutos: int = 30,
    paciente=None,
    especialidad=None,
    especialista=None
) -> Cita:
    """
    Agenda una cita desde recepción o portal paciente.
    Acepta tanto IDs como instancias de modelos para paciente, especialidad y especialista.
    """
    if paciente is None:
        if isinstance(paciente_id, Paciente):
            paciente = paciente_id
        elif paciente_id is not None:
            paciente = Paciente.objects.get(id=int(paciente_id))
    elif isinstance(paciente, (int, str)) and str(paciente).isdigit():
        paciente = Paciente.objects.get(id=int(paciente))

    if paciente is None:
        raise ValueError("Es necesario especificar un paciente válido para agendar la cita.")

    if especialidad is None:
        if isinstance(especialidad_id, Especialidad):
            especialidad = especialidad_id
        elif especialidad_id is not None:
            especialidad = Especialidad.objects.get(id=int(especialidad_id))
    elif isinstance(especialidad, (int, str)) and str(especialidad).isdigit():
        especialidad = Especialidad.objects.get(id=int(especialidad))

    if especialista is None and especialista_id is not None:
        if isinstance(especialista_id, Especialista):
            especialista = especialista_id
        elif str(especialista_id).isdigit():
            especialista = Especialista.objects.select_related('consultorio', 'consultorio_asignado', 'usuario').get(id=int(especialista_id))
    elif isinstance(especialista, (int, str)) and str(especialista).isdigit():
        especialista = Especialista.objects.select_related('consultorio', 'consultorio_asignado', 'usuario').get(id=int(especialista))

    if not especialidad and especialista:
        especialidad = especialista.especialidad

    if not especialidad:
        raise ValueError("Es necesario seleccionar una especialidad médica.")

    fecha_hora_fin = fecha_hora_inicio + timedelta(minutes=duracion_minutos)

    fecha_dia = fecha_hora_inicio.date()
    inicio_dia = timezone.make_aware(datetime.combine(fecha_dia, time.min))
    fin_dia = timezone.make_aware(datetime.combine(fecha_dia, time.max))

    if especialista:
        consultorio = especialista.consultorio or especialista.consultorio_asignado
        if not consultorio:
            raise ValueError(f"El especialista Dr/Dra. {especialista.usuario.nombre_completo} no tiene un consultorio asignado.")

        conflicto = Cita.objects.filter(
            especialista=especialista,
            fecha_hora_inicio__lt=fecha_hora_fin,
            fecha_hora_fin__gt=fecha_hora_inicio,
            estado_cita__in=[EstadoCita.PROGRAMADA, EstadoCita.EN_SALA]
        ).exists()

        if conflicto:
            raise ValueError(f"El médico Dr/Dra. {especialista.usuario.nombre_completo} ya posee una cita en esa franja horaria.")
    else:
        # Asignación Automática por Menor Carga del Día con Desempate Aleatorio
        from django.db.models import Q
        medicos_especialidad = Especialista.objects.select_related('consultorio', 'consultorio_asignado', 'usuario').filter(
            Q(consultorio__isnull=False) | Q(consultorio_asignado__isnull=False),
            especialidad=especialidad,
            usuario__estado_cuenta=True
        )

        if not medicos_especialidad.exists():
            raise ValueError("No existen médicos activos asignados a consultorio para esta especialidad.")

        # Filtrar médicos libres en el horario
        medicos_libres = []
        for esp in medicos_especialidad:
            traslape = Cita.objects.filter(
                especialista=esp,
                fecha_hora_inicio__lt=fecha_hora_fin,
                fecha_hora_fin__gt=fecha_hora_inicio,
                estado_cita__in=[EstadoCita.PROGRAMADA, EstadoCita.EN_SALA]
            ).exists()

            if not traslape:
                cant_citas_dia = Cita.objects.filter(
                    especialista=esp,
                    fecha_hora_inicio__gte=inicio_dia,
                    fecha_hora_inicio__lte=fin_dia,
                    estado_cita__in=[EstadoCita.PROGRAMADA, EstadoCita.EN_SALA, EstadoCita.ATENDIDA]
                ).count()
                medicos_libres.append((esp, cant_citas_dia))

        if not medicos_libres:
            raise ValueError("No hay ningún médico disponible en esa franja horaria para la especialidad seleccionada.")

        # Encontrar la cantidad mínima de citas entre los médicos libres
        min_citas = min(item[1] for item in medicos_libres)

        # Filtrar los médicos empatados en el número mínimo de citas
        candidatos_minimos = [item[0] for item in medicos_libres if item[1] == min_citas]

        # Si hay empate, seleccionar uno al azar (random)
        especialista = random.choice(candidatos_minimos)
        consultorio = especialista.consultorio or especialista.consultorio_asignado

    cita = Cita.objects.create(
        paciente=paciente,
        especialista=especialista,
        consultorio=consultorio,
        fecha_hora_inicio=fecha_hora_inicio,
        fecha_hora_fin=fecha_hora_fin,
        estado_cita=EstadoCita.PROGRAMADA
    )
    from agendamiento.services.notificaciones_service import enviar_correo_confirmacion_cita
    enviar_correo_confirmacion_cita(cita)
    return cita


def obtener_horarios_disponibles(
    fecha: date,
    especialidad_id: int,
    especialista_id: int = None
) -> list[dict]:
    """
    Retorna la lista de TODAS las franjas horarias de 30 minutos (08:00 AM a 05:00 PM).
    - disponible=True: Libre para seleccionar (verde/teal).
    - disponible=False: Ocupado / Pasado (rojo/disabled).
    """
    franjas = []
    horas_posibles = [
        time(8, 0), time(8, 30), time(9, 0), time(9, 30),
        time(10, 0), time(10, 30), time(11, 0), time(11, 30),
        time(14, 0), time(14, 30), time(15, 0), time(15, 30),
        time(16, 0), time(16, 30), time(17, 0)
    ]

    ahora = timezone.now()

    if isinstance(fecha, str):
        fecha = datetime.strptime(fecha, '%Y-%m-%d').date()

    for h in horas_posibles:
        dt_inicio = timezone.make_aware(datetime.combine(fecha, h))

        dt_fin = dt_inicio + timedelta(minutes=30)
        es_pasado = dt_inicio < ahora

        if especialista_id:
            medico = Especialista.objects.filter(id=especialista_id, consultorio__isnull=False).first()
            if not medico or es_pasado:
                franjas.append({
                    'hora': h.strftime('%H:%M'),
                    'hora_display': h.strftime('%I:%M %p'),
                    'disponible': False
                })
                continue

            ocupado = Cita.objects.filter(
                especialista=medico,
                fecha_hora_inicio__lt=dt_fin,
                fecha_hora_fin__gt=dt_inicio,
                estado_cita__in=[EstadoCita.PROGRAMADA, EstadoCita.EN_SALA]
            ).exists()

            franjas.append({
                'hora': h.strftime('%H:%M'),
                'hora_display': h.strftime('%I:%M %p'),
                'disponible': not ocupado
            })
        else:
            if es_pasado:
                franjas.append({
                    'hora': h.strftime('%H:%M'),
                    'hora_display': h.strftime('%I:%M %p'),
                    'disponible': False
                })
                continue

            medicos = Especialista.objects.filter(
                especialidad_id=especialidad_id,
                usuario__estado_cuenta=True,
                consultorio__isnull=False
            )

            if not medicos.exists():
                franjas.append({
                    'hora': h.strftime('%H:%M'),
                    'hora_display': h.strftime('%I:%M %p'),
                    'disponible': False
                })
                continue

            al_menos_uno_libre = False
            for esp in medicos:
                ocupado = Cita.objects.filter(
                    especialista=esp,
                    fecha_hora_inicio__lt=dt_fin,
                    fecha_hora_fin__gt=dt_inicio,
                    estado_cita__in=[EstadoCita.PROGRAMADA, EstadoCita.EN_SALA]
                ).exists()
                if not ocupado:
                    al_menos_uno_libre = True
                    break

            franjas.append({
                'hora': h.strftime('%H:%M'),
                'hora_display': h.strftime('%I:%M %p'),
                'disponible': al_menos_uno_libre
            })

    return franjas


@transaction.atomic
def reprogramar_cita_recepcion(
    cita_id: int,
    nueva_fecha_hora: datetime,
    nuevo_especialista_id: int = None
) -> Cita:
    """
    Reprograma una cita existente desde recepción.
    """
    cita = Cita.objects.select_related('paciente', 'especialista').get(id=cita_id)

    if nuevo_especialista_id:
        especialista = Especialista.objects.select_related('consultorio').get(id=nuevo_especialista_id)
    else:
        especialista = cita.especialista

    duracion = cita.fecha_hora_fin - cita.fecha_hora_inicio
    nueva_fecha_fin = nueva_fecha_hora + duracion

    cita.especialista = especialista
    cita.consultorio = especialista.consultorio
    cita.fecha_hora_inicio = nueva_fecha_hora
    cita.fecha_hora_fin = nueva_fecha_fin
    cita.estado_cita = EstadoCita.PROGRAMADA
    cita.save()

    return cita


@transaction.atomic
def reubicar_cita_contingencia(
    cita_id: int,
    nuevo_especialista_id: int,
    nueva_fecha_hora: datetime
) -> Cita:
    """
    Reubica una cita en estado 'Pendiente_Reubicacion' asignándole un nuevo especialista o fecha/hora (RN08).
    """
    cita = Cita.objects.select_related('paciente').get(id=cita_id)
    nuevo_especialista = Especialista.objects.select_related('consultorio').get(id=nuevo_especialista_id)

    if not nuevo_especialista.consultorio:
        raise ValueError(f"El especialista {nuevo_especialista.usuario.nombre_completo} no posee un consultorio asignado.")

    duracion = cita.fecha_hora_fin - cita.fecha_hora_inicio
    nueva_fecha_fin = nueva_fecha_hora + duracion

    cita.especialista = nuevo_especialista
    cita.consultorio = nuevo_especialista.consultorio
    cita.fecha_hora_inicio = nueva_fecha_hora
    cita.fecha_hora_fin = nueva_fecha_fin
    cita.estado_cita = EstadoCita.PROGRAMADA
    cita.save()

    return cita


def validar_reprogramacion(cita, nueva_fecha_hora):
    """
    RN01: Máximo 1 reprogramación desde autogestión web del paciente.
    RN02: Anticipación mayor a 24 horas para la nueva fecha elegida.
    """
    if cita.contador_reprogramacion >= 1:
        return False, "RN01: Has alcanzado el límite de 1 reprogramación permitida."

    ahora = timezone.now()
    if timezone.is_naive(nueva_fecha_hora):
        nueva_fecha_hora = timezone.make_aware(nueva_fecha_hora)

    # La nueva fecha/hora elegida debe tener al menos 24h de anticipación desde el momento actual
    if (nueva_fecha_hora - ahora).total_seconds() < 86400:
        return False, "La nueva fecha y hora elegida debe ser con al menos 24 horas de anticipación."

    return True, "Reprogramación válida."


@transaction.atomic
def atender_y_guardar_notas_cita(cita_id, especialista, notas_clinicas: str = "") -> Cita:
    """
    HU05: Pasa el estado de la cita a 'Atendida' y registra las notas clínicas/observaciones del paciente.
    """
    from django.core.exceptions import ValidationError

    if isinstance(cita_id, Cita):
        cita_obj = cita_id
    else:
        cita_obj = Cita.objects.select_related('paciente__usuario', 'especialista').get(id=cita_id)

    if hasattr(especialista, 'perfil_especialista'):
        esp_obj = especialista.perfil_especialista
    else:
        esp_obj = especialista

    if cita_obj.especialista_id != esp_obj.id:
        raise PermissionError("Esta cita no pertenece a tu agenda médica.")

    if cita_obj.estado_cita != EstadoCita.ATENDIDA and cita_obj.estado_cita != EstadoCita.EN_SALA:
        raise ValidationError("Solo se pueden registrar notas clínicas en citas Atendidas o En Sala.")

    cita_obj.estado_cita = EstadoCita.ATENDIDA
    if notas_clinicas is not None:
        cita_obj.notas_clinicas = notas_clinicas.strip()
    cita_obj.save()
    return cita_obj


@transaction.atomic
def agendar_cita_web(paciente, especialista, consultorio, fecha_hora_inicio, duracion_minutos=30):
    """Agendamiento web autónomo del paciente (HU02)."""
    from django.core.exceptions import ValidationError

    inasistencias = getattr(paciente, 'contador_inasistencias', 0)
    if inasistencias >= 3 or getattr(paciente, 'bloqueado_agendamiento_web', False):
        raise ValidationError("RN04: Tu agendamiento web ha sido bloqueado por haber acumulado 3 inasistencias.")

    fecha_hora_fin = fecha_hora_inicio + timedelta(minutes=duracion_minutos)
    cita = Cita.objects.create(
        paciente=paciente,
        especialista=especialista,
        consultorio=consultorio,
        fecha_hora_inicio=fecha_hora_inicio,
        fecha_hora_fin=fecha_hora_fin,
        estado_cita=EstadoCita.PROGRAMADA
    )
    return cita


@transaction.atomic
def reprogramar_cita(cita, nueva_fecha_hora_inicio, es_recepcion=False):
    """Reprogramación de citas web (HU03, RN01, RN02)."""
    from django.core.exceptions import ValidationError
    from agendamiento.services.notificaciones_service import enviar_correo_reprogramacion_cita
    if not es_recepcion:
        es_valido, msg = validar_reprogramacion(cita, nueva_fecha_hora_inicio)
        if not es_valido:
            raise ValidationError(msg)
        cita.contador_reprogramacion += 1

    duracion = cita.fecha_hora_fin - cita.fecha_hora_inicio
    nueva_fecha_fin = nueva_fecha_hora_inicio + duracion

    cita.fecha_hora_inicio = nueva_fecha_hora_inicio
    cita.fecha_hora_fin = nueva_fecha_fin
    cita.estado_cita = EstadoCita.PROGRAMADA
    cita.save()

    # Notificación por correo al paciente
    enviar_correo_reprogramacion_cita(cita)
    return cita


@transaction.atomic
def cancelar_cita(cita, es_recepcion=False):
    """Cancelación de cita web (RN02)."""
    from django.core.exceptions import ValidationError
    from agendamiento.services.notificaciones_service import enviar_correo_cancelacion_cita
    if not es_recepcion:
        ahora = timezone.now()
        if (cita.fecha_hora_inicio - ahora).total_seconds() < 86400:
            raise ValidationError("Las cancelaciones deben realizarse con más de 24 horas de anticipación.")
    cita.estado_cita = EstadoCita.CANCELADA
    cita.save()

    # Notificación por correo al paciente
    enviar_correo_cancelacion_cita(cita)
    return cita


@transaction.atomic
def unirse_lista_espera(paciente, especialista=None, especialidad=None):
    """Inscripción en lista de espera (HU09)."""
    from agendamiento.models import ListaEspera
    espera = ListaEspera.objects.create(
        paciente=paciente,
        especialista=especialista,
        especialidad=especialidad
    )
    return espera


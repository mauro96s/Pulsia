"""
Servicio para la gestión de solicitudes de permisos y contingencias de ausencia médica.
Implementa las reglas de negocio RN05 (Conflicto por Ausencias) y RN08 / HU14 (Contingencia por Ausencia de Emergencia).
Soporta Auto-Reubicación Inteligente en tiempo real y anticipada con envío de notificaciones por correo (HU10).
"""

from datetime import date, datetime, timedelta
from django.utils import timezone
from django.db import transaction
from agendamiento.models import (
    Especialista, EstadoTurno, Cita, EstadoCita, AusenciasPermisos, EstadoAprobacion
)

@transaction.atomic
def auto_reubicar_cita_inteligente(cita_id: int, priorizar_mismo_dia: bool = True) -> tuple[bool, Cita, str]:
    """
    Algoritmo de Auto-Reubicación Inteligente para Citas Afectadas (RN05 / RN08).
    1. Identifica la especialidad de la cita y busca otros médicos activos de esa especialidad.
    2. Si priorizar_mismo_dia=True, busca médicos con estado_turno='Presente' hoy y hueco disponible.
    3. Si no hay cupo hoy o se evalúa a futuro, recorre días siguientes (omitendo festivos) buscando el primer cupo disponible.
    4. Actualiza la cita con el nuevo médico, consultorio, fecha y hora.
    5. Dispara el correo electrónico formal de notificación al paciente (HU10).
    Returns (exito: bool, cita: Cita, mensaje: str)
    """
    from agendamiento.services.citas_service import obtener_horarios_disponibles
    from agendamiento.services.festivos_service import es_dia_festivo
    from agendamiento.services.notificaciones_service import enviar_correo_reubicacion_cita

    cita = Cita.objects.select_related(
        'paciente__usuario', 'especialista__usuario', 'especialista__especialidad', 'consultorio'
    ).get(id=cita_id)

    medico_original = cita.especialista
    especialidad = medico_original.especialidad
    duracion = cita.fecha_hora_fin - cita.fecha_hora_inicio

    medicos_candidatos = Especialista.objects.select_related(
        'usuario', 'consultorio_asignado', 'consultorio'
    ).filter(
        especialidad=especialidad,
        usuario__estado_cuenta=True
    ).exclude(id=medico_original.id)

    if not medicos_candidatos.exists():
        return False, cita, f"No existen otros especialistas activos para la especialidad {especialidad.nombre_especialidad}."

    fecha_original = cita.fecha_hora_inicio.date()
    hora_original = cita.fecha_hora_inicio.time()
    ahora = timezone.now()

    # --- PASO 1: Intentar Reubicación en el Mismo Día (Si priorizar_mismo_dia=True) ---
    if priorizar_mismo_dia and fecha_original >= ahora.date():
        medicos_presentes = [m for m in medicos_candidatos if m.estado_turno == EstadoTurno.PRESENTE]
        
        for esp in medicos_presentes:
            consultorio = esp.consultorio_asignado or esp.consultorio
            if not consultorio:
                continue

            inicio_propuesto = timezone.make_aware(datetime.combine(fecha_original, hora_original))
            fin_propuesto = inicio_propuesto + duracion

            conflicto = Cita.objects.filter(
                especialista=esp,
                fecha_hora_inicio__lt=fin_propuesto,
                fecha_hora_fin__gt=inicio_propuesto,
                estado_cita__in=[EstadoCita.PROGRAMADA, EstadoCita.EN_SALA]
            ).exists()

            if not conflicto:
                cita.especialista = esp
                cita.consultorio = consultorio
                cita.fecha_hora_inicio = inicio_propuesto
                cita.fecha_hora_fin = fin_propuesto
                cita.estado_cita = EstadoCita.EN_SALA if cita.estado_cita == EstadoCita.EN_SALA else EstadoCita.PROGRAMADA
                cita.save()
                
                enviar_correo_reubicacion_cita(cita, medico_anterior=medico_original, motivo="atención de contingencia el mismo día")
                return True, cita, f"Reubicado automáticamente hoy con Dr/Dra. {esp.usuario.nombre_completo} (Consultorio {consultorio.nombre_codigo})."

    # --- PASO 2: Búsqueda en Días Futuros (Primer Cupo Disponible) ---
    fecha_evaluar = fecha_original if not priorizar_mismo_dia else fecha_original + timedelta(days=1)
    max_dias_busqueda = 30

    for _ in range(max_dias_busqueda):
        es_festivo, _ = es_dia_festivo(fecha_evaluar)
        if fecha_evaluar.weekday() != 6 and not es_festivo:
            franjas = obtener_horarios_disponibles(fecha_evaluar, especialidad_id=especialidad.id)
            franjas_libres = [f for f in franjas if f.get('disponible')]

            if franjas_libres:
                franja_elegida = franjas_libres[0]
                hora_partes = [int(x) for x in franja_elegida['hora'].split(':')]
                hora_eval = datetime.min.time().replace(hour=hora_partes[0], minute=hora_partes[1])
                
                dt_inicio = timezone.make_aware(datetime.combine(fecha_evaluar, hora_eval))
                dt_fin = dt_inicio + duracion

                for esp in medicos_candidatos:
                    consultorio = esp.consultorio_asignado or esp.consultorio
                    if not consultorio:
                        continue

                    conflicto = Cita.objects.filter(
                        especialista=esp,
                        fecha_hora_inicio__lt=dt_fin,
                        fecha_hora_fin__gt=dt_inicio,
                        estado_cita__in=[EstadoCita.PROGRAMADA, EstadoCita.EN_SALA]
                    ).exists()

                    if not conflicto:
                        cita.especialista = esp
                        cita.consultorio = consultorio
                        cita.fecha_hora_inicio = dt_inicio
                        cita.fecha_hora_fin = dt_fin
                        cita.estado_cita = EstadoCita.PROGRAMADA
                        cita.save()

                        enviar_correo_reubicacion_cita(cita, medico_anterior=medico_original, motivo="reubicación anticipada por novedad médica")
                        return True, cita, f"Reubicado automáticamente para el {dt_inicio.strftime('%d/%m/%Y %I:%M %p')} con Dr/Dra. {esp.usuario.nombre_completo}."

        fecha_evaluar += timedelta(days=1)

    return False, cita, "No se encontró ningún cupo disponible en los próximos 30 días para esta especialidad."


@transaction.atomic
def procesar_auto_reubicacion_lote(citas_list: list[Cita]) -> tuple[int, int, list[str]]:
    """
    Ejecuta el algoritmo de auto-reubicación inteligente en lote para un conjunto de citas.
    Returns (exitosos, fallidos, lista_de_mensajes)
    """
    exitosos = 0
    fallidos = 0
    mensajes = []

    for cita in citas_list:
        exito, cita_updated, msg = auto_reubicar_cita_inteligente(cita.id, priorizar_mismo_dia=True)
        if exito:
            exitosos += 1
            mensajes.append(f"Cita #{cita.id} ({cita.paciente.usuario.nombre_completo}): {msg}")
        else:
            fallidos += 1
            mensajes.append(f"Cita #{cita.id} ({cita.paciente.usuario.nombre_completo}): {msg}")

    return exitosos, fallidos, mensajes


@transaction.atomic
def declarar_ausencia_emergencia(especialista_id: int, fecha: date = None) -> tuple[int, list[Cita], int]:
    """
    HU14 / RN08: Declara la ausencia médica de emergencia de un especialista para el día de hoy (o fecha dada).
    1. Marca el estado de turno del médico como 'Ausente'.
    2. Cambia todas las citas agendadas del día a estado 'Pendiente_Reubicacion'.
    3. Ejecuta la Auto-Reubicación Inteligente Automática en Lote y envía correos electrónicos a los pacientes.
    Returns (cantidad_citas_afectadas, lista_de_citas, cantidad_reubicadas_automaticamente)
    """
    if fecha is None:
        fecha = timezone.now().date()

    if isinstance(especialista_id, Especialista):
        especialista = especialista_id
    else:
        especialista = Especialista.objects.get(id=especialista_id)
    especialista.estado_turno = EstadoTurno.AUSENTE
    especialista.save()

    inicio_dia = timezone.make_aware(datetime.combine(fecha, datetime.min.time()))
    fin_dia = timezone.make_aware(datetime.combine(fecha, datetime.max.time()))

    citas_afectadas_qs = Cita.objects.select_related('paciente__usuario', 'especialista__usuario', 'consultorio').filter(
        especialista=especialista,
        fecha_hora_inicio__gte=inicio_dia,
        fecha_hora_fin__lte=fin_dia,
        estado_cita__in=[EstadoCita.PROGRAMADA, EstadoCita.EN_SALA]
    )

    citas_list = list(citas_afectadas_qs)
    cant_afectadas = len(citas_list)

    # Actualizar estado a Pendiente de Reubicación
    citas_afectadas_qs.update(estado_cita=EstadoCita.PENDIENTE_REUBICACION)

    # Ejecutar Auto-Reubicación Inteligente Masiva
    reubicadas, fallidas, _ = procesar_auto_reubicacion_lote(citas_list)

    return cant_afectadas, citas_list, reubicadas


@transaction.atomic
def procesar_aprobacion_permiso(permiso_id: int, aprobar: bool) -> tuple[AusenciasPermisos, int, int]:
    """
    HU04 / RN05: Aprueba o rechaza una solicitud de permiso previa (aviso con anticipación del médico).
    Al ser APROBADA:
    1. Evalúa las citas agendadas en ese rango de fechas futuro.
    2. Pasa las citas a 'Pendiente_Reubicacion'.
    3. Ejecuta AUTO-REUBICACIÓN INTELIGENTE buscando los primeros cupos disponibles con otros especialistas y enviando correos electrónicos a cada paciente.
    Returns (permiso_obj, cantidad_citas_en_conflicto, cantidad_reubicadas_auto)
    """
    permiso = AusenciasPermisos.objects.select_related('especialista__usuario').get(id=permiso_id)

    if not aprobar:
        permiso.estado_aprobacion = EstadoAprobacion.RECHAZADO
        permiso.save()
        return permiso, 0, 0

    permiso.estado_aprobacion = EstadoAprobacion.APROBADO
    permiso.save()

    citas_conflicto_qs = Cita.objects.select_related('paciente__usuario', 'especialista__usuario', 'consultorio').filter(
        especialista=permiso.especialista,
        fecha_hora_inicio__gte=permiso.fecha_hora_inicio,
        fecha_hora_fin__lte=permiso.fecha_hora_fin,
        estado_cita=EstadoCita.PROGRAMADA
    )

    citas_list = list(citas_conflicto_qs)
    cant_conflictos = len(citas_list)
    
    if cant_conflictos > 0:
        citas_conflicto_qs.update(estado_cita=EstadoCita.PENDIENTE_REUBICACION)
        # Ejecutar auto-reubicación masiva en lote con envío de correos
        reubicadas_auto, _, _ = procesar_auto_reubicacion_lote(citas_list)
    else:
        reubicadas_auto = 0

    return permiso, cant_conflictos, reubicadas_auto


def solicitar_permiso_especialista(
    especialista: Especialista,
    fecha_hora_inicio: datetime,
    fecha_hora_fin: datetime,
    motivo_solicitud: str
) -> AusenciasPermisos:
    """
    HU04: Permite al especialista registrar una solicitud de permiso o ausencia médica (estado Pendiente).
    """
    return AusenciasPermisos.objects.create(
        especialista=especialista,
        fecha_hora_inicio=fecha_hora_inicio,
        fecha_hora_fin=fecha_hora_fin,
        motivo_solicitud=motivo_solicitud.strip(),
        estado_aprobacion=EstadoAprobacion.PENDIENTE
    )

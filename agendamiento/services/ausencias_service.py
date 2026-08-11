"""
Servicio para la gestión de solicitudes de permisos y contingencias de ausencia médica.
Implementa las reglas de negocio RN05 (Conflicto por Ausencias) y RN08 / HU14 (Contingencia por Ausencia de Emergencia).
"""

from datetime import date, datetime
from django.utils import timezone
from agendamiento.models import (
    Especialista, EstadoTurno, Cita, EstadoCita, AusenciasPermisos, EstadoAprobacion
)

def declarar_ausencia_emergencia(especialista_id: int, fecha: date = None) -> tuple[int, list[Cita]]:
    """
    HU14 / RN08: Declara la ausencia médica de emergencia de un especialista para el día de hoy (o fecha dada).
    1. Marca el estado de turno del médico como 'Ausente'.
    2. Cambia todas las citas agendadas del día a estado 'Pendiente_Reubicacion'.
    3. Garantiza que la reubicación institucional no consuma el contador de reprogramación del paciente (RN08).
    Returns (cantidad_citas_afectadas, lista_de_citas)
    """
    if fecha is None:
        fecha = timezone.now().date()

    especialista = Especialista.objects.get(id=especialista_id)
    especialista.estado_turno = EstadoTurno.AUSENTE
    especialista.save()

    # Filtrar citas del médico en esa fecha que estén activas
    inicio_dia = timezone.make_aware(datetime.combine(fecha, datetime.min.time()))
    fin_dia = timezone.make_aware(datetime.combine(fecha, datetime.max.time()))

    citas_afectadas_qs = Cita.objects.select_related('paciente__usuario', 'consultorio').filter(
        especialista=especialista,
        fecha_hora_inicio__gte=inicio_dia,
        fecha_hora_fin__lte=fin_dia,
        estado_cita__in=[EstadoCita.PROGRAMADA, EstadoCita.EN_SALA]
    )

    citas_list = list(citas_afectadas_qs)
    cant_afectadas = len(citas_list)

    # Actualizar estado a Pendiente de Reubicación
    citas_afectadas_qs.update(estado_cita=EstadoCita.PENDIENTE_REUBICACION)

    return cant_afectadas, citas_list


def procesar_aprobacion_permiso(permiso_id: int, aprobar: bool) -> tuple[AusenciasPermisos, int]:
    """
    HU04 / RN05: Aprueba o rechaza una solicitud de permiso y evalúa conflictos con citas agendadas.
    Al ser aprobada, si existen citas agendadas en la franja, se pasan a 'Pendiente_Reubicacion'.
    Returns (permiso_obj, cantidad_citas_en_conflicto)
    """
    permiso = AusenciasPermisos.objects.select_related('especialista__usuario').get(id=permiso_id)

    if not aprobar:
        permiso.estado_aprobacion = EstadoAprobacion.RECHAZADO
        permiso.save()
        return permiso, 0

    permiso.estado_aprobacion = EstadoAprobacion.APROBADO
    permiso.save()

    # Evaluar conflicto con citas programadas en la franja de ausencia
    citas_conflicto = Cita.objects.filter(
        especialista=permiso.especialista,
        fecha_hora_inicio__gte=permiso.fecha_hora_inicio,
        fecha_hora_fin__lte=permiso.fecha_hora_fin,
        estado_cita=EstadoCita.PROGRAMADA
    )

    cant_conflictos = citas_conflicto.count()
    if cant_conflictos > 0:
        citas_conflicto.update(estado_cita=EstadoCita.PENDIENTE_REUBICACION)

    return permiso, cant_conflictos

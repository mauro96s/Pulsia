"""
Controladores / Vistas para la gestión del Rol Especialista Médico (Pulsia Medical Systems).
HU04 (Solicitud de Ausencias), HU05 (Notas Clínicas / Historial), HU13 (Check-in de Asistencia).
"""

from datetime import datetime
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
    solicitar_permiso_especialista
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
    Dashboard del Especialista Médico (HU04, HU05, HU13).
    Sigue estrictamente las historias de usuario de HU_RN.md y la guía de estilos visuales.
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

    # 2. Citas del Especialista para el Día
    inicio_dia = timezone.make_aware(datetime.combine(fecha_sel, datetime.min.time()))
    fin_dia = timezone.make_aware(datetime.combine(fecha_sel, datetime.max.time()))

    citas_qs = Cita.objects.select_related(
        'paciente__usuario', 'consultorio'
    ).filter(
        especialista=especialista,
        fecha_hora_inicio__gte=inicio_dia,
        fecha_hora_inicio__lte=fin_dia
    ).order_by('fecha_hora_inicio')

    # Contadores por Estado Oficial
    cant_total = citas_qs.count()
    cant_en_sala = citas_qs.filter(estado_cita=EstadoCita.EN_SALA).count()
    cant_atendidas = citas_qs.filter(estado_cita=EstadoCita.ATENDIDA).count()

    # 3. Solicitudes de Permiso (HU04)
    permisos = AusenciasPermisos.objects.filter(especialista=especialista).order_by('-fecha_hora_inicio')[:10]

    context = {
        'especialista': especialista,
        'fecha_seleccionada': fecha_sel.strftime('%Y-%m-%d'),
        'fecha_actual_display': fecha_sel,
        'citas': citas_qs,
        'cant_total': cant_total,
        'cant_en_sala': cant_en_sala,
        'cant_atendidas': cant_atendidas,
        'permisos': permisos,
        'EstadoCita': EstadoCita,
        'EstadoTurno': EstadoTurno,
        'EstadoAprobacion': EstadoAprobacion,
    }

    return render(request, 'agendamiento/dashboard/especialista.html', context)


@login_required(login_url='login')
@require_POST
def especialista_checkin_turno_view(request):
    """
    HU13: Check-in Médico (Inicio de Turno).
    Pasa el estado_turno a 'Presente' o 'Ausente'.
    """
    especialista = obtener_perfil_especialista(request.user)
    if not especialista:
        messages.error(request, "Perfil médico no encontrado.")
        return redirect('dashboard_especialista')

    especialista = marcar_checkin_medico(especialista.id)
    estado_txt = "PRESENTE (Turno Iniciado)" if especialista.estado_turno == EstadoTurno.PRESENTE else "AUSENTE (Turno Finalizado)"
    messages.success(request, f"Estado de turno actualizado: {estado_txt}")
    return redirect('dashboard_especialista')


@login_required(login_url='login')
@require_POST
def especialista_atender_cita_view(request, cita_id):
    """
    HU05: Historial y Anotaciones Clínicas.
    Recibe las notas clínicas/observaciones, cambia el estado de la cita a 'Atendida' y guarda la información.
    """
    especialista = obtener_perfil_especialista(request.user)
    if not especialista:
        messages.error(request, "Perfil médico no encontrado.")
        return redirect('dashboard_especialista')

    notas_clinicas = request.POST.get('notas_clinicas', '').strip()

    try:
        cita = atender_y_guardar_notas_cita(cita_id, especialista, notas_clinicas)
        messages.success(request, f"✅ Cita atendida exitosamente para {cita.paciente.usuario.nombre_completo}. Notas clínicas guardadas.")
    except Exception as e:
        messages.error(request, str(e))

    return redirect('dashboard_especialista')


@login_required(login_url='login')
@require_POST
def especialista_solicitar_permiso_view(request):
    """
    HU04: Gestión de Permisos e Imprevistos del Médico.
    Crea una nueva solicitud de permiso en la tabla ausencias_permisos con estado 'Pendiente'.
    """
    especialista = obtener_perfil_especialista(request.user)
    if not especialista:
        messages.error(request, "Perfil médico no encontrado.")
        return redirect('dashboard_especialista')

    fecha_inicio_str = request.POST.get('fecha_inicio', '')
    hora_inicio_str = request.POST.get('hora_inicio', '08:00')
    fecha_fin_str = request.POST.get('fecha_fin', '')
    hora_fin_str = request.POST.get('hora_fin', '18:00')
    motivo = request.POST.get('motivo_solicitud', '').strip()

    if not fecha_inicio_str or not fecha_fin_str or not motivo:
        messages.error(request, "Por favor diligencia todos los campos requeridos del permiso.")
        return redirect('dashboard_especialista')

    try:
        inicio_dt = timezone.make_aware(datetime.strptime(f"{fecha_inicio_str} {hora_inicio_str}", "%Y-%m-%d %H:%M"))
        fin_dt = timezone.make_aware(datetime.strptime(f"{fecha_fin_str} {hora_fin_str}", "%Y-%m-%d %H:%M"))

        if fin_dt <= inicio_dt:
            messages.error(request, "La fecha/hora fin debe ser posterior a la fecha/hora inicio.")
            return redirect('dashboard_especialista')

        solicitar_permiso_especialista(especialista, inicio_dt, fin_dt, motivo)
        messages.success(request, "Solicitud de permiso registrada correctamente. Queda en estado Pendiente para aprobación de administración.")
    except ValueError:
        messages.error(request, "Formato de fecha u hora inválido.")
    except Exception as e:
        messages.error(request, str(e))

    return redirect('dashboard_especialista')

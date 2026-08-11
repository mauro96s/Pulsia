"""
Controladores / Vistas para la gestión de citas y operaciones del Rol Recepcionista (Pulsia Medical Systems).
"""

from datetime import datetime, date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone

from agendamiento.models import (
    Cita, EstadoCita, Paciente, Especialista, Especialidad, Consultorio,
    RolUsuario, EstadoTurno, CustomUser, TipoDocumento
)
from agendamiento.services import (
    evaluar_tolerancia_cita,
    marcar_llegada_paciente,
    marcar_checkin_medico,
    registrar_inasistencia,
    crear_paciente_expres,
    agendar_cita_recepcion_balanceada,
    obtener_horarios_disponibles,
    reprogramar_cita_recepcion,
    reubicar_cita_contingencia
)


def es_recepcionista_o_admin(user) -> bool:
    return user.is_authenticated and user.rol in [RolUsuario.RECEPCIONISTA, RolUsuario.ADMINISTRADOR]


@login_required(login_url='login')
def recepcion_dashboard_view(request):
    """
    Dashboard de Recepción y Control de Asistencia Global del Día.
    Pantalla limpia enfocada en el flujo diario de llegada y check-in.
    """
    if not es_recepcionista_o_admin(request.user):
        messages.error(request, "Acceso no autorizado al módulo de Recepción.")
        return redirect('dashboard')

    # 1. Filtros de Fecha
    fecha_str = request.GET.get('fecha', '')
    if fecha_str:
        try:
            fecha_sel = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            fecha_sel = timezone.now().date()
    else:
        fecha_sel = timezone.now().date()

    # 2. Monitoreo y Búsqueda de Médicos
    especialistas = Especialista.objects.select_related(
        'usuario', 'especialidad', 'consultorio'
    ).filter(usuario__estado_cuenta=True)

    medico_query = request.GET.get('medico_q', '').strip()
    if medico_query:
        especialistas = especialistas.filter(
            Q(usuario__nombre_completo__icontains=medico_query) |
            Q(especialidad__nombre_especialidad__icontains=medico_query)
        )

    cant_totales_medicos = especialistas.count()
    cant_presentes_medicos = especialistas.filter(estado_turno=EstadoTurno.PRESENTE).count()

    # 3. Consulta de Citas del Día
    inicio_dia = timezone.make_aware(datetime.combine(fecha_sel, datetime.min.time()))
    fin_dia = timezone.make_aware(datetime.combine(fecha_sel, datetime.max.time()))

    citas_qs = Cita.objects.select_related(
        'paciente__usuario', 'especialista__usuario', 'especialista__especialidad', 'consultorio'
    ).filter(
        fecha_hora_inicio__gte=inicio_dia,
        fecha_hora_inicio__lte=fin_dia
    ).order_by('fecha_hora_inicio')

    # Filtro por Especialidad
    filtro_especialidad = request.GET.get('especialidad', '')
    if filtro_especialidad and filtro_especialidad.isdigit():
        citas_qs = citas_qs.filter(especialista__especialidad_id=int(filtro_especialidad))

    # Filtro por Estado
    filtro_estado = request.GET.get('estado', '')
    if filtro_estado:
        citas_qs = citas_qs.filter(estado_cita=filtro_estado)

    # Búsqueda por Paciente (Nombre o Cédula)
    search_query = request.GET.get('q', '').strip()
    if search_query:
        citas_qs = citas_qs.filter(
            Q(paciente__usuario__nombre_completo__icontains=search_query) |
            Q(paciente__usuario__num_documento__icontains=search_query)
        )

    # 4. Evaluación de Tolerancia de 10 minutos
    citas_con_tolerancia = []
    hora_actual = timezone.now()

    for cita in citas_qs:
        info_tolerancia = evaluar_tolerancia_cita(cita, hora_actual)
        citas_con_tolerancia.append({
            'cita': cita,
            'tolerancia': info_tolerancia
        })

    # Catálogos
    especialidades = Especialidad.objects.all()
    cant_pendientes_reubicacion = Cita.objects.filter(
        estado_cita=EstadoCita.PENDIENTE_REUBICACION
    ).count()

    context = {
        'fecha_seleccionada': fecha_sel.strftime('%Y-%m-%d'),
        'fecha_actual_display': fecha_sel,
        'especialistas': especialistas,
        'medico_query': medico_query,
        'cant_totales_medicos': cant_totales_medicos,
        'cant_presentes_medicos': cant_presentes_medicos,
        'citas_con_tolerancia': citas_con_tolerancia,
        'especialidades': especialidades,
        'filtro_especialidad': filtro_especialidad,
        'filtro_estado': filtro_estado,
        'search_query': search_query,
        'estados_cita': EstadoCita.choices,
        'cant_pendientes_reubicacion': cant_pendientes_reubicacion,
        'tipos_documento': TipoDocumento.choices,
    }

    return render(request, 'agendamiento/dashboard/recepcion.html', context)


@login_required(login_url='login')
def recepcion_agenda_global_view(request):
    """
    Vista principal de la Agenda Global del Recepcionista:
    Igual al inicio del Administrador pero con botones para Agendar y Reagendar Citas.
    Muestra el Calendario General con filtros por Especialidad, Especialista y Paciente.
    """
    if not es_recepcionista_o_admin(request.user):
        messages.error(request, "Acceso no autorizado.")
        return redirect('dashboard')

    especialidades = Especialidad.objects.all()
    especialistas = Especialista.objects.select_related('usuario', 'especialidad').filter(
        usuario__estado_cuenta=True
    )
    pacientes = Paciente.objects.select_related('usuario').filter(
        usuario__estado_cuenta=True
    ).order_by('usuario__nombre_completo')

    context = {
        'especialidades': especialidades,
        'especialistas': especialistas,
        'pacientes': pacientes,
    }
    return render(request, 'agendamiento/citas/agenda_global.html', context)


@login_required(login_url='login')
def recepcion_agendar_reprogramar_view(request):

    """
    Nuevo Módulo de Agendamiento y Reprogramación de Citas para Recepción.
    - Izquierda: Calendario interactivo de fechas.
    - Derecha: Selección de Especialidad primero, luego Especialista (o Asignación Automática por Menor Carga).
    - Reprogramación de citas buscando por documento del paciente.
    """
    if not es_recepcionista_o_admin(request.user):
        messages.error(request, "Acceso no autorizado.")
        return redirect('dashboard')

    if request.method == 'POST':
        cita_id = request.POST.get('cita_id')
        paciente_id = request.POST.get('paciente_id')
        especialidad_id = request.POST.get('especialidad_id')
        especialista_id = request.POST.get('especialista_id') or None
        fecha_str = request.POST.get('fecha_cita') or request.POST.get('fecha_nueva')
        hora_str = request.POST.get('hora_cita') or request.POST.get('hora_nueva')

        if not paciente_id or not especialidad_id or not fecha_str or not hora_str:
            messages.error(request, "Todos los campos obligatorios deben completarse.")
            return redirect('recepcion_agendar_cita')

        try:
            dt_inicio = datetime.strptime(f"{fecha_str} {hora_str}", "%Y-%m-%d %H:%M")
            dt_inicio_aware = timezone.make_aware(dt_inicio)
            esp_id_int = int(especialista_id) if especialista_id and especialista_id.isdigit() else None

            if cita_id and cita_id.isdigit():
                # REAGENDAMIENTO DE CITA EXISTENTE
                cita = reprogramar_cita_recepcion(
                    cita_id=int(cita_id),
                    nueva_fecha_hora=dt_inicio_aware,
                    nuevo_especialista_id=esp_id_int
                )
                messages.success(
                    request,
                    f"¡Cita #{cita.id} reagendada con éxito! Paciente: {cita.paciente.usuario.nombre_completo} | "
                    f"Nuevo médico: Dr/Dra. {cita.especialista.usuario.nombre_completo} | "
                    f"Fecha: {fecha_str} {hora_str} (Consultorio {cita.consultorio.nombre_codigo})."
                )
            else:
                # AGENDAMIENTO DE NUEVA CITA
                cita = agendar_cita_recepcion_balanceada(
                    paciente_id=int(paciente_id),
                    especialidad_id=int(especialidad_id),
                    fecha_hora_inicio=dt_inicio_aware,
                    especialista_id=esp_id_int
                )
                messages.success(
                    request,
                    f"¡Cita agendada con éxito! Paciente: {cita.paciente.usuario.nombre_completo} | "
                    f"Médico asignado: Dr/Dra. {cita.especialista.usuario.nombre_completo} | "
                    f"Fecha: {fecha_str} {hora_str} (Consultorio {cita.consultorio.nombre_codigo})."
                )
        except ValueError as ve:
            messages.error(request, str(ve))
        except Exception as e:
            messages.error(request, f"Error al procesar la cita: {str(e)}")

        return redirect('recepcion_agenda_global')


    # GET: Cargar datos iniciales y pre-cargar cita si viene por parámetro para reagendar
    fecha_sel = request.GET.get('fecha', timezone.now().strftime('%Y-%m-%d'))
    especialidades = Especialidad.objects.all()
    especialistas = Especialista.objects.select_related('usuario', 'especialidad', 'consultorio').filter(
        usuario__estado_cuenta=True
    )
    pacientes = Paciente.objects.select_related('usuario').filter(usuario__estado_cuenta=True)[:30]

    cita_preCargada = None
    cita_id_param = request.GET.get('cita_id')
    if cita_id_param and cita_id_param.isdigit():
        cita_obj = Cita.objects.select_related('paciente__usuario', 'especialista__especialidad').filter(id=int(cita_id_param)).first()
        if cita_obj:
            cita_preCargada = {
                'id': cita_obj.id,
                'paciente_id': cita_obj.paciente.id,
                'paciente_nombre': cita_obj.paciente.usuario.nombre_completo,
                'paciente_doc': cita_obj.paciente.usuario.num_documento or '',
                'especialidad_id': cita_obj.especialista.especialidad.id if cita_obj.especialista and cita_obj.especialista.especialidad else '',
                'especialista_id': cita_obj.especialista.id,
                'fecha_ymd': cita_obj.fecha_hora_inicio.strftime('%Y-%m-%d'),
                'hora_hm': cita_obj.fecha_hora_inicio.strftime('%H:%M'),
            }
            fecha_sel = cita_obj.fecha_hora_inicio.strftime('%Y-%m-%d')

    context = {
        'fecha_seleccionada': fecha_sel,
        'especialidades': especialidades,
        'especialistas': especialistas,
        'pacientes': pacientes,
        'tipos_documento': TipoDocumento.choices,
        'cita_preCargada': cita_preCargada,
    }

    return render(request, 'agendamiento/citas/agendar_reprogramar.html', context)


@login_required(login_url='login')
def api_horarios_disponibles_view(request):
    """API JSON que calcula y retorna franjas horarias disponibles para una fecha y especialidad."""
    if not es_recepcionista_o_admin(request.user):
        return JsonResponse({'success': False, 'error': 'No autorizado'}, status=403)

    fecha_str = request.GET.get('fecha')
    especialidad_id = request.GET.get('especialidad_id')
    especialista_id = request.GET.get('especialista_id') or None

    if not fecha_str or not especialidad_id:
        return JsonResponse({'success': True, 'horarios': []})


    try:
        fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        esp_id = int(especialidad_id)
        esp_med_id = int(especialista_id) if especialista_id and especialista_id.isdigit() else None

        horarios = obtener_horarios_disponibles(
            fecha=fecha_obj,
            especialidad_id=esp_id,
            especialista_id=esp_med_id
        )
        return JsonResponse({'success': True, 'horarios': horarios})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required(login_url='login')
def api_buscar_citas_paciente_view(request):
    """API JSON para buscar citas activas de un paciente ingresando su número de documento."""
    if not es_recepcionista_o_admin(request.user):
        return JsonResponse({'success': False, 'error': 'No autorizado'}, status=403)

    q = request.GET.get('q', '').strip()
    if not q:
        return JsonResponse({'success': True, 'citas': []})

    citas_qs = Cita.objects.select_related(
        'paciente__usuario', 'especialista__usuario', 'especialista__especialidad', 'consultorio'
    ).filter(
        Q(paciente__usuario__num_documento__icontains=q) |
        Q(paciente__usuario__nombre_completo__icontains=q),
        estado_cita__in=[EstadoCita.PROGRAMADA, EstadoCita.PENDIENTE_REUBICACION]
    ).order_by('fecha_hora_inicio')

    resultados = []
    for c in citas_qs:
        resultados.append({
            'id': c.id,
            'fecha_hora_str': c.fecha_hora_inicio.strftime('%Y-%m-%d %I:%M %p'),
            'fecha_ymd': c.fecha_hora_inicio.strftime('%Y-%m-%d'),
            'hora_hm': c.fecha_hora_inicio.strftime('%H:%M'),
            'paciente_nombre': c.paciente.usuario.nombre_completo,
            'paciente_doc': c.paciente.usuario.num_documento or '',
            'especialista_id': c.especialista.id,
            'especialista_nombre': c.especialista.usuario.nombre_completo,
            'especialidad_id': c.especialista.especialidad.id,
            'especialidad_nombre': c.especialista.especialidad.nombre_especialidad,
            'consultorio_codigo': c.consultorio.nombre_codigo,
            'estado_cita': c.get_estado_cita_display()
        })

    return JsonResponse({'success': True, 'citas': resultados})


@login_required(login_url='login')
def api_especialistas_por_especialidad_view(request):
    """API JSON que lista especialistas activos de una especialidad."""
    if not es_recepcionista_o_admin(request.user):
        return JsonResponse({'success': False, 'error': 'No autorizado'}, status=403)

    especialidad_id = request.GET.get('especialidad_id')
    if not especialidad_id:
        return JsonResponse({'success': True, 'especialistas': []})

    medicos = Especialista.objects.select_related('usuario', 'consultorio').filter(
        especialidad_id=especialidad_id,
        usuario__estado_cuenta=True
    )

    resultados = []
    for esp in medicos:
        resultados.append({
            'id': esp.id,
            'nombre_completo': esp.usuario.nombre_completo,
            'consultorio': esp.consultorio.nombre_codigo if esp.consultorio else 'Sin Consultorio'
        })

    return JsonResponse({'success': True, 'especialistas': resultados})


@login_required(login_url='login')
@require_POST
def recepcion_checkin_medico_view(request, especialista_id):
    """Acción POST para registrar o alternar manualmente la asistencia (check-in) de un médico."""
    if not es_recepcionista_o_admin(request.user):
        messages.error(request, "Acceso denegado.")
        return redirect('dashboard')

    nuevo_estado = request.POST.get('nuevo_estado', None)
    try:
        medico = marcar_checkin_medico(especialista_id, nuevo_estado)
        if medico.estado_turno == EstadoTurno.PRESENTE:
            messages.success(request, f"Dr/Dra. {medico.usuario.nombre_completo} registrado como PRESENTE en consultorio {medico.consultorio.nombre_codigo if medico.consultorio else 'N/A'}.")
        else:
            messages.warning(request, f"Dr/Dra. {medico.usuario.nombre_completo} marcado como SIN CHECK-IN / AUSENTE.")
    except Exception as e:
        messages.error(request, f"Error al actualizar asistencia del médico: {str(e)}")

    redirect_url = request.POST.get('redirect_to', 'dashboard_recepcion')
    return redirect(redirect_url)


@login_required(login_url='login')
@require_POST
def recepcion_anunciar_llegada_view(request, cita_id):
    """Acción POST para anunciar la llegada del paciente a recepción."""
    if not es_recepcionista_o_admin(request.user):
        messages.error(request, "Acceso denegado.")
        return redirect('dashboard')

    try:
        cita, es_prioridad, msg = marcar_llegada_paciente(cita_id)
        if es_prioridad:
            messages.warning(request, msg)
        else:
            messages.success(request, msg)
    except Exception as e:
        messages.error(request, f"Error al registrar la llegada: {str(e)}")

    redirect_url = request.POST.get('redirect_to', 'dashboard_recepcion')
    return redirect(redirect_url)


@login_required(login_url='login')
@require_POST
def recepcion_marcar_inasistencia_view(request, cita_id):
    """Acción POST para registrar inasistencia por superar 10 min de retraso."""
    if not es_recepcionista_o_admin(request.user):
        messages.error(request, "Acceso denegado.")
        return redirect('dashboard')

    try:
        cita, cuenta_bloqueada = registrar_inasistencia(cita_id)
        if cuenta_bloqueada:
            messages.warning(
                request,
                f"Inasistencia registrada para {cita.paciente.usuario.nombre_completo}. "
                f"⚠️ El paciente acumuló 3 inasistencias y su cuenta ha sido deshabilitada."
            )
        else:
            messages.info(
                request,
                f"Inasistencia registrada para {cita.paciente.usuario.nombre_completo}. "
                f"Inasistencias acumuladas: {cita.paciente.contador_inasistencias}/3."
            )
    except Exception as e:
        messages.error(request, f"Error al marcar la inasistencia: {str(e)}")

    redirect_url = request.POST.get('redirect_to', 'dashboard_recepcion')
    return redirect(redirect_url)


@login_required(login_url='login')
def recepcion_buscar_paciente_api(request):
    """API JSON para buscar pacientes por número de documento o nombre."""
    if not es_recepcionista_o_admin(request.user):
        return JsonResponse({'success': False, 'error': 'Acceso no autorizado'}, status=403)

    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse({'success': True, 'pacientes': []})

    pacientes_qs = Paciente.objects.select_related('usuario').filter(
        Q(usuario__num_documento__icontains=q) |
        Q(usuario__nombre_completo__icontains=q)
    )[:10]

    resultados = []
    for p in pacientes_qs:
        resultados.append({
            'id': p.id,
            'nombre_completo': p.usuario.nombre_completo,
            'tipo_documento': p.usuario.tipo_documento or 'CC',
            'num_documento': p.usuario.num_documento or '',
            'correo': p.usuario.correo,
            'telefono': p.usuario.telefono or '',
            'contador_inasistencias': p.contador_inasistencias,
            'estado_cuenta': p.usuario.estado_cuenta
        })

    return JsonResponse({'success': True, 'pacientes': resultados})


@login_required(login_url='login')
@require_POST
def recepcion_crear_paciente_expres_view(request):
    """Acción POST para registrar un nuevo paciente rápidamente desde la recepción."""
    if not es_recepcionista_o_admin(request.user):
        messages.error(request, "Acceso no autorizado.")
        return redirect('dashboard')

    nombre_completo = request.POST.get('nombre_completo', '').strip()
    tipo_documento = request.POST.get('tipo_documento', TipoDocumento.CC)
    num_documento = request.POST.get('num_documento', '').strip()
    correo = request.POST.get('correo', '').strip()
    telefono = request.POST.get('telefono', '').strip()
    fecha_nac_str = request.POST.get('fecha_nacimiento', '')

    if not nombre_completo or not correo or not num_documento:
        messages.error(request, "Los campos Nombre Completo, Documento y Correo son obligatorios.")
        return redirect('recepcion_agendar_reprogramar')

    if CustomUser.objects.filter(correo=correo).exists():
        messages.error(request, "Ya existe un usuario con este correo electrónico.")
        return redirect('recepcion_agendar_reprogramar')

    if CustomUser.objects.filter(num_documento=num_documento).exists():
        messages.error(request, "Ya existe un paciente con este número de documento.")
        return redirect('recepcion_agendar_reprogramar')

    fecha_nac = None
    if fecha_nac_str:
        try:
            fecha_nac = datetime.strptime(fecha_nac_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    try:
        paciente = crear_paciente_expres(
            nombre_completo=nombre_completo,
            tipo_documento=tipo_documento,
            num_documento=num_documento,
            correo=correo,
            telefono=telefono,
            fecha_nacimiento=fecha_nac
        )
        messages.success(
            request,
            f"Paciente {paciente.usuario.nombre_completo} registrado exitosamente en el sistema."
        )
    except Exception as e:
        messages.error(request, f"Error al registrar paciente: {str(e)}")

    return redirect('recepcion_agendar_reprogramar')


@login_required(login_url='login')
def recepcion_bandeja_reubicacion_view(request):
    """Vista de la Bandeja de Reubicación Institucional de Citas."""
    if not es_recepcionista_o_admin(request.user):
        messages.error(request, "Acceso no autorizado.")
        return redirect('dashboard')

    citas_pendientes = Cita.objects.select_related(
        'paciente__usuario', 'especialista__usuario', 'especialista__especialidad', 'consultorio'
    ).filter(
        estado_cita=EstadoCita.PENDIENTE_REUBICACION
    ).order_by('fecha_hora_inicio')

    especialistas_activos = Especialista.objects.select_related(
        'usuario', 'especialidad', 'consultorio'
    ).filter(
        usuario__estado_cuenta=True
    )

    context = {
        'citas_pendientes': citas_pendientes,
        'cant_pendientes': citas_pendientes.count(),
        'especialistas_activos': especialistas_activos,
    }
    return render(request, 'agendamiento/citas/reubicacion.html', context)


@login_required(login_url='login')
@require_POST
def recepcion_reubicar_cita_view(request, cita_id):
    """Acción POST para reubicar una cita a una nueva fecha o especialista sin penalizar al paciente."""
    if not es_recepcionista_o_admin(request.user):
        messages.error(request, "Acceso no autorizado.")
        return redirect('dashboard')

    nuevo_especialista_id = request.POST.get('especialista_id')
    fecha_str = request.POST.get('fecha_nueva')
    hora_str = request.POST.get('hora_nueva')

    if not nuevo_especialista_id or not fecha_str or not hora_str:
        messages.error(request, "Por favor completa la nueva fecha, hora y especialista.")
        return redirect('recepcion_bandeja_reubicacion')

    try:
        dt_inicio = datetime.strptime(f"{fecha_str} {hora_str}", "%Y-%m-%d %H:%M")
        dt_inicio_aware = timezone.make_aware(dt_inicio)

        cita = reubicar_cita_contingencia(
            cita_id=cita_id,
            nuevo_especialista_id=int(nuevo_especialista_id),
            nueva_fecha_hora=dt_inicio_aware
        )

        messages.success(
            request,
            f"Cita de {cita.paciente.usuario.nombre_completo} reubicada exitosamente para el {fecha_str} a las {hora_str}."
        )
    except Exception as e:
        messages.error(request, f"Error al reubicar la cita: {str(e)}")

    return redirect('recepcion_bandeja_reubicacion')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Q, Count
import json
from datetime import datetime
from django.utils import timezone

from agendamiento.models import (
    CustomUser, RolUsuario, TipoDocumento,
    Paciente, Especialidad, Consultorio, Especialista,
    HorarioLaboral, Cita, EstadoCita, AusenciasPermisos, EstadoAprobacion
)
from agendamiento.services import obtener_festivos_colombia, declarar_ausencia_emergencia


def is_admin(user):
    return user.is_authenticated and (user.rol == RolUsuario.ADMINISTRADOR or user.is_superuser)


# ==========================================
# 1. DASHBOARD PRINCIPAL (INICIO)
# ==========================================
@login_required(login_url='login')
def admin_dashboard_view(request):
    """Dashboard Principal del Administrador: Métricas clave y Calendario General."""
    if not is_admin(request.user):
        messages.error(request, "Acceso restringido únicamente a administradores.")
        return redirect('dashboard')

    especialidades = Especialidad.objects.all()
    especialistas = Especialista.objects.select_related('usuario', 'especialidad').filter(usuario__is_active=True)
    pacientes_count = Paciente.objects.filter(usuario__is_active=True).count()

    # Métricas BI Clave
    total_citas = Cita.objects.count()
    total_atendidas = Cita.objects.filter(estado_cita=EstadoCita.ATENDIDA).count()
    total_programadas = Cita.objects.filter(estado_cita=EstadoCita.PROGRAMADA).count()
    total_en_sala = Cita.objects.filter(estado_cita=EstadoCita.EN_SALA).count()
    total_inasistencias = Cita.objects.filter(estado_cita=EstadoCita.NO_ASISTIO).count()
    total_canceladas = Cita.objects.filter(estado_cita=EstadoCita.CANCELADA).count()

    tasa_atencion = round((total_atendidas / total_citas * 100), 1) if total_citas > 0 else 0
    tasa_inasistencia = round((total_inasistencias / total_citas * 100), 1) if total_citas > 0 else 0

    context = {
        'especialidades': especialidades,
        'especialistas': especialistas,
        'pacientes_count': pacientes_count,
        'total_citas': total_citas,
        'total_atendidas': total_atendidas,
        'total_programadas': total_programadas,
        'total_en_sala': total_en_sala,
        'total_inasistencias': total_inasistencias,
        'total_canceladas': total_canceladas,
        'tasa_atencion': tasa_atencion,
        'tasa_inasistencia': tasa_inasistencia,
    }
    return render(request, 'agendamiento/dashboard/admin.html', context)


# ==========================================
# 2. GESTIÓN UNIFICADA DE USUARIOS (ESPECIALISTAS, RECEPCIONISTAS, PACIENTES, ADMINS)
# ==========================================
@login_required(login_url='login')
def admin_usuarios_view(request):
    """Index de Usuarios: Tabla unificada para Especialistas, Recepcionistas, Pacientes y Administradores."""
    if not is_admin(request.user):
        messages.error(request, "Acceso restringido a administradores.")
        return redirect('dashboard')

    q = request.GET.get('q', '').strip()
    rol_filtro = request.GET.get('rol', '').strip()
    estado = request.GET.get('estado', '').strip()
    especialidad_id = request.GET.get('especialidad', '').strip()

    usuarios_qs = CustomUser.objects.select_related(
        'perfil_especialista',
        'perfil_especialista__especialidad',
        'perfil_especialista__consultorio',
        'perfil_paciente'
    ).all().order_by('-date_joined')

    if q:
        usuarios_qs = usuarios_qs.filter(
            Q(nombre_completo__icontains=q) |
            Q(num_documento__icontains=q) |
            Q(correo__icontains=q) |
            Q(telefono__icontains=q)
        )

    if rol_filtro:
        usuarios_qs = usuarios_qs.filter(rol__iexact=rol_filtro)

    if estado == 'activo':
        usuarios_qs = usuarios_qs.filter(is_active=True)
    elif estado == 'inactivo':
        usuarios_qs = usuarios_qs.filter(is_active=False)

    if especialidad_id and (not rol_filtro or rol_filtro.lower() == 'especialista'):
        usuarios_qs = usuarios_qs.filter(perfil_especialista__especialidad_id=especialidad_id)

    especialidades = Especialidad.objects.all()
    consultorios = Consultorio.objects.filter(estado_operativo=True)
    tipos_documento = TipoDocumento.choices
    roles = RolUsuario.choices

    context = {
        'usuarios': usuarios_qs,
        'especialidades': especialidades,
        'consultorios': consultorios,
        'tipos_documento': tipos_documento,
        'roles': roles,
        'q': q,
        'rol_filtro': rol_filtro,
        'estado': estado,
        'especialidad_id': especialidad_id,
    }
    return render(request, 'agendamiento/admin/usuarios.html', context)


# Alias de retrocompatibilidad
admin_especialistas_view = admin_usuarios_view


@login_required(login_url='login')
@require_POST
def admin_crear_usuario(request):
    """POST: Crear cualquier tipo de usuario en el sistema (Especialista, Recepcionista, Paciente, Administrador)."""
    if not is_admin(request.user):
        return JsonResponse({'success': False, 'error': 'Acceso denegado.'}, status=403)

    nombre_completo = request.POST.get('nombre_completo', '').strip()
    tipo_doc = request.POST.get('tipo_documento', TipoDocumento.CC)
    num_doc = request.POST.get('num_documento', '').strip()
    correo = request.POST.get('correo', '').strip()
    telefono = request.POST.get('telefono', '').strip()
    password = request.POST.get('password', '123456')
    rol = request.POST.get('rol', RolUsuario.ESPECIALISTA)
    especialidad_id = request.POST.get('especialidad_id')
    consultorio_id = request.POST.get('consultorio_id')

    if not nombre_completo or not correo or not num_doc or not rol:
        messages.error(request, "Por favor completa todos los campos obligatorios.")
        return redirect('admin_usuarios')

    if CustomUser.objects.filter(correo=correo).exists():
        messages.error(request, "Ya existe un usuario con este correo electrónico.")
        return redirect('admin_usuarios')

    if CustomUser.objects.filter(num_documento=num_doc).exists():
        messages.error(request, "Ya existe un usuario registrado con ese número de documento.")
        return redirect('admin_usuarios')

    user = CustomUser.objects.create_user(
        username=correo,
        correo=correo,
        nombre_completo=nombre_completo,
        tipo_documento=tipo_doc,
        num_documento=num_doc,
        telefono=telefono,
        rol=rol,
        password=password
    )

    if rol == RolUsuario.ESPECIALISTA:
        if especialidad_id:
            especialidad = get_object_or_404(Especialidad, id=especialidad_id)
            consultorio = Consultorio.objects.filter(id=consultorio_id).first() if consultorio_id else None
            especialista = Especialista.objects.create(
                usuario=user,
                especialidad=especialidad,
                consultorio=consultorio
            )
            for dia in range(1, 6):
                HorarioLaboral.objects.create(
                    especialista=especialista,
                    dia_semana=dia,
                    hora_inicio="08:00",
                    hora_fin="17:00",
                    hora_inicio_descanso="12:00",
                    hora_fin_descanso="13:00"
                )
    elif rol == RolUsuario.PACIENTE:
        from datetime import datetime, date
        from agendamiento.models.pacientes import Paciente
        fecha_nac_str = request.POST.get('fecha_nacimiento')
        fecha_nac = date(1995, 1, 1)
        if fecha_nac_str:
            try:
                fecha_nac = datetime.strptime(fecha_nac_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        Paciente.objects.create(
            usuario=user,
            fecha_nacimiento=fecha_nac,
            acepta_habeas_data=True
        )

    messages.success(request, f"Usuario {nombre_completo} ({rol}) registrado exitosamente.")
    return redirect('admin_usuarios')


# Alias de retrocompatibilidad
admin_crear_especialista = admin_crear_usuario


@login_required(login_url='login')
@require_POST
def admin_editar_usuario(request, usuario_id):
    """POST: Editar perfil, rol, contraseña y datos de cualquier usuario."""
    if not is_admin(request.user):
        return JsonResponse({'success': False, 'error': 'Acceso denegado.'}, status=403)

    usuario = get_object_or_404(CustomUser, id=usuario_id)

    nombre_completo = request.POST.get('nombre_completo', '').strip()
    tipo_doc = request.POST.get('tipo_documento', usuario.tipo_documento)
    num_doc = request.POST.get('num_documento', '').strip()
    correo = request.POST.get('correo', '').strip()
    telefono = request.POST.get('telefono', '').strip()
    nuevo_rol = request.POST.get('rol', usuario.rol)
    is_active = request.POST.get('is_active') == 'on'
    especialidad_id = request.POST.get('especialidad_id')
    consultorio_id = request.POST.get('consultorio_id')

    if not nombre_completo or not correo:
        messages.error(request, "Nombre y correo electrónico son requeridos.")
        return redirect('admin_usuarios')

    if correo != usuario.correo and CustomUser.objects.filter(correo=correo).exists():
        messages.error(request, "El correo electrónico ya pertenece a otro usuario.")
        return redirect('admin_usuarios')

    if num_doc != usuario.num_documento and CustomUser.objects.filter(num_documento=num_doc).exists():
        messages.error(request, "El número de documento ya pertenece a otro usuario.")
        return redirect('admin_usuarios')

    nueva_password = request.POST.get('nueva_password', '').strip()
    if nueva_password:
        usuario.set_password(nueva_password)

    usuario.nombre_completo = nombre_completo
    usuario.tipo_documento = tipo_doc
    usuario.num_documento = num_doc
    usuario.correo = correo
    usuario.username = correo
    usuario.telefono = telefono
    usuario.rol = nuevo_rol
    usuario.is_active = is_active
    usuario.estado_cuenta = is_active
    usuario.save()

    # Si es Especialista, actualizar o crear su perfil
    if nuevo_rol == RolUsuario.ESPECIALISTA:
        if especialidad_id:
            especialidad = get_object_or_404(Especialidad, id=especialidad_id)
            consultorio = Consultorio.objects.filter(id=consultorio_id).first() if consultorio_id else None
            esp_profile, _ = Especialista.objects.get_or_create(usuario=usuario, defaults={'especialidad': especialidad})
            esp_profile.especialidad = especialidad
            esp_profile.consultorio = consultorio
            esp_profile.save()
    elif nuevo_rol == RolUsuario.PACIENTE:
        from datetime import datetime, date
        from agendamiento.models.pacientes import Paciente
        fecha_nac_str = request.POST.get('fecha_nacimiento')
        pac_profile, _ = Paciente.objects.get_or_create(
            usuario=usuario,
            defaults={'fecha_nacimiento': date(1995, 1, 1), 'acepta_habeas_data': True}
        )
        if fecha_nac_str:
            try:
                pac_profile.fecha_nacimiento = datetime.strptime(fecha_nac_str, '%Y-%m-%d').date()
                pac_profile.save()
            except ValueError:
                pass

    messages.success(request, f"Usuario {nombre_completo} actualizado correctamente.")
    return redirect('admin_usuarios')


# Alias de retrocompatibilidad
def admin_editar_especialista(request, especialista_id):
    esp = get_object_or_404(Especialista, id=especialista_id)
    return admin_editar_usuario(request, esp.usuario.id)


@login_required(login_url='login')
@require_POST
def admin_eliminar_usuario(request, usuario_id):
    """POST: Dar de baja o eliminar un usuario."""
    if not is_admin(request.user):
        return JsonResponse({'success': False, 'error': 'Acceso denegado.'}, status=403)

    usuario = get_object_or_404(CustomUser, id=usuario_id)

    if usuario == request.user:
        messages.error(request, "No puedes dar de baja tu propia cuenta de administrador.")
        return redirect('admin_usuarios')

    tiene_citas = False
    if hasattr(usuario, 'perfil_especialista'):
        tiene_citas = Cita.objects.filter(especialista=usuario.perfil_especialista).exists()
    elif hasattr(usuario, 'perfil_paciente'):
        tiene_citas = Cita.objects.filter(paciente=usuario.perfil_paciente).exists()

    if tiene_citas:
        usuario.is_active = False
        usuario.estado_cuenta = False
        usuario.save()
        messages.warning(
            request,
            f"El usuario {usuario.nombre_completo} fue DADO DE BAJA (desactivado) conservando su historial."
        )
    else:
        nombre = usuario.nombre_completo
        usuario.delete()
        messages.success(request, f"El usuario {nombre} fue eliminado del sistema.")

    return redirect('admin_usuarios')


# Alias de retrocompatibilidad
def admin_eliminar_especialista(request, especialista_id):
    esp = get_object_or_404(Especialista, id=especialista_id)
    return admin_eliminar_usuario(request, esp.usuario.id)


# ==========================================
# 3. ESTRUCTURA MÉDICA (ESPECIALIDADES Y CONSULTORIOS)
# ==========================================
@login_required(login_url='login')
def admin_estructura_medica_view(request):
    """Index de Estructura Médica: Especialidades y Consultorios Físicos."""
    if not is_admin(request.user):
        messages.error(request, "Acceso restringido a administradores.")
        return redirect('dashboard')

    q_esp = request.GET.get('q_esp', '').strip()
    q_cons = request.GET.get('q_cons', '').strip()
    tab = request.GET.get('tab', '').strip()

    if not tab:
        if q_cons:
            tab = 'cons'
        else:
            tab = 'esp'

    especialidades_qs = Especialidad.objects.annotate(
        num_especialistas=Count('especialistas', distinct=True)
    )
    if q_esp:
        especialidades_qs = especialidades_qs.filter(
            Q(nombre_especialidad__icontains=q_esp) | Q(descripcion__icontains=q_esp)
        )

    consultorios_qs = Consultorio.objects.annotate(
        num_citas=Count('cita', distinct=True)
    )
    if q_cons:
        consultorios_qs = consultorios_qs.filter(nombre_codigo__icontains=q_cons)

    context = {
        'especialidades': especialidades_qs,
        'consultorios': consultorios_qs,
        'q_esp': q_esp,
        'q_cons': q_cons,
        'tab': tab,
    }
    return render(request, 'agendamiento/admin/estructura_medica.html', context)


# Alias de retrocompatibilidad
admin_catalogos_view = admin_estructura_medica_view


# ==========================================
# 4. MÓDULO DE ASIGNACIONES (CONSULTORIOS Y HORARIOS LABORALES)
# ==========================================
@login_required(login_url='login')
def admin_asignaciones_view(request):
    """Index de Asignaciones Médicas: Consultorios Asignados y Horarios Laborales."""
    if not is_admin(request.user):
        messages.error(request, "Acceso restringido a administradores.")
        return redirect('dashboard')

    q_cons = request.GET.get('q_cons', '').strip()
    q_hor = request.GET.get('q_hor', '').strip()
    tab = request.GET.get('tab', '').strip()

    if not tab:
        if q_hor:
            tab = 'hor'
        else:
            tab = 'cons'

    especialistas_qs = Especialista.objects.select_related('usuario', 'especialidad', 'consultorio').all()
    if q_cons:
        especialistas_qs = especialistas_qs.filter(
            Q(usuario__nombre_completo__icontains=q_cons) |
            Q(especialidad__nombre_especialidad__icontains=q_cons) |
            Q(consultorio__nombre_codigo__icontains=q_cons)
        )

    especialistas_horarios_qs = Especialista.objects.select_related('usuario', 'especialidad').prefetch_related('horarios').all()
    if q_hor:
        especialistas_horarios_qs = especialistas_horarios_qs.filter(
            Q(usuario__nombre_completo__icontains=q_hor) |
            Q(especialidad__nombre_especialidad__icontains=q_hor)
        )

    especialidades = Especialidad.objects.all()
    consultorios = Consultorio.objects.all()

    context = {
        'especialistas': especialistas_qs,
        'especialistas_horarios': especialistas_horarios_qs,
        'especialidades': especialidades,
        'consultorios': consultorios,
        'q_cons': q_cons,
        'q_hor': q_hor,
        'tab': tab,
    }
    return render(request, 'agendamiento/admin/asignaciones.html', context)


@login_required(login_url='login')
@require_POST
def admin_asignar_medico(request, especialista_id):
    """POST: Asignar o modificar la especialidad y el consultorio de un médico especialista."""
    if not is_admin(request.user):
        return JsonResponse({'success': False, 'error': 'Acceso denegado.'}, status=403)

    especialista = get_object_or_404(Especialista, id=especialista_id)
    especialidad_id = request.POST.get('especialidad_id')
    consultorio_id = request.POST.get('consultorio_id')

    if especialidad_id:
        especialista.especialidad = get_object_or_404(Especialidad, id=especialidad_id)

    if consultorio_id:
        especialista.consultorio = Consultorio.objects.filter(id=consultorio_id).first()
    else:
        especialista.consultorio = None

    especialista.save()
    messages.success(request, f"Asignación actualizada para el Dr/Dra. {especialista.usuario.nombre_completo}.")
    return redirect('admin_asignaciones')


@login_required(login_url='login')
@require_POST
def admin_guardar_horario(request):
    """POST: Guardar o actualizar la jornada de Horarios Laborales de un médico especialista."""
    if not is_admin(request.user):
        return JsonResponse({'success': False, 'error': 'Acceso denegado.'}, status=403)

    especialista_id = request.POST.get('especialista_id')
    especialista = get_object_or_404(Especialista, id=especialista_id)

    dias_seleccionados = request.POST.getlist('dias')
    hora_inicio = request.POST.get('hora_inicio')
    hora_fin = request.POST.get('hora_fin')
    hora_inicio_descanso = request.POST.get('hora_inicio_descanso') or None
    hora_fin_descanso = request.POST.get('hora_fin_descanso') or None

    if not dias_seleccionados or not hora_inicio or not hora_fin:
        messages.error(request, "Debes seleccionar al menos un día y especificar hora de inicio y fin.")
        return redirect('/administracion/asignaciones/?tab=hor')

    for dia_str in dias_seleccionados:
        try:
            dia_int = int(dia_str)
            HorarioLaboral.objects.update_or_create(
                especialista=especialista,
                dia_semana=dia_int,
                defaults={
                    'hora_inicio': hora_inicio,
                    'hora_fin': hora_fin,
                    'hora_inicio_descanso': hora_inicio_descanso,
                    'hora_fin_descanso': hora_fin_descanso,
                }
            )
        except ValueError:
            continue

    messages.success(request, f"Horario laboral actualizado exitosamente para el Dr/Dra. {especialista.usuario.nombre_completo}.")
    return redirect('/administracion/asignaciones/?tab=hor')


@login_required(login_url='login')
@require_POST
def admin_crear_especialidad(request):
    """POST: Crear nueva especialidad médica."""
    if not is_admin(request.user):
        return JsonResponse({'success': False, 'error': 'Acceso denegado.'}, status=403)

    nombre = request.POST.get('nombre_especialidad', '').strip()
    descripcion = request.POST.get('descripcion', '').strip()

    if not nombre:
        messages.error(request, "El nombre de la especialidad es obligatorio.")
        return redirect('admin_estructura_medica')

    if Especialidad.objects.filter(nombre_especialidad__iexact=nombre).exists():
        messages.warning(request, f"La especialidad '{nombre}' ya se encuentra registrada.")
        return redirect('admin_estructura_medica')

    Especialidad.objects.create(nombre_especialidad=nombre, descripcion=descripcion)
    messages.success(request, f"Especialidad '{nombre}' registrada con éxito.")
    return redirect('admin_estructura_medica')


@login_required(login_url='login')
@require_POST
def admin_editar_especialidad(request, especialidad_id):
    """POST: Editar especialidad médica."""
    if not is_admin(request.user):
        return JsonResponse({'success': False, 'error': 'Acceso denegado.'}, status=403)

    especialidad = get_object_or_404(Especialidad, id=especialidad_id)
    nombre = request.POST.get('nombre_especialidad', '').strip()
    descripcion = request.POST.get('descripcion', '').strip()

    if not nombre:
        messages.error(request, "El nombre de la especialidad no puede estar vacío.")
        return redirect('admin_estructura_medica')

    especialidad.nombre_especialidad = nombre
    especialidad.descripcion = descripcion
    especialidad.save()

    messages.success(request, f"Especialidad '{nombre}' actualizada correctamente.")
    return redirect('admin_estructura_medica')


@login_required(login_url='login')
@require_POST
def admin_eliminar_especialidad(request, especialidad_id):
    """POST: Eliminar especialidad."""
    if not is_admin(request.user):
        return JsonResponse({'success': False, 'error': 'Acceso denegado.'}, status=403)

    especialidad = get_object_or_404(Especialidad, id=especialidad_id)

    if especialidad.especialistas.exists():
        messages.error(
            request,
            f"No se puede eliminar '{especialidad.nombre_especialidad}' porque tiene especialistas médicos asignados."
        )
    else:
        nombre = especialidad.nombre_especialidad
        especialidad.delete()
        messages.success(request, f"Especialidad '{nombre}' eliminada con éxito.")

    return redirect('admin_estructura_medica')


@login_required(login_url='login')
@require_POST
def admin_crear_consultorio(request):
    """POST: Crear nuevo consultorio físico."""
    if not is_admin(request.user):
        return JsonResponse({'success': False, 'error': 'Acceso denegado.'}, status=403)

    codigo = request.POST.get('nombre_codigo', '').strip()
    estado = request.POST.get('estado_operativo') == 'on'

    if not codigo:
        messages.error(request, "El código/número de consultorio es obligatorio.")
        return redirect('admin_estructura_medica')

    if Consultorio.objects.filter(nombre_codigo=codigo).exists():
        messages.error(request, f"El consultorio '{codigo}' ya está registrado.")
        return redirect('admin_estructura_medica')

    Consultorio.objects.create(nombre_codigo=codigo, estado_operativo=estado)
    messages.success(request, f"Consultorio '{codigo}' registrado exitosamente.")
    return redirect('admin_estructura_medica')


@login_required(login_url='login')
@require_POST
def admin_editar_consultorio(request, consultorio_id):
    """POST: Editar consultorio físico."""
    if not is_admin(request.user):
        return JsonResponse({'success': False, 'error': 'Acceso denegado.'}, status=403)

    consultorio = get_object_or_404(Consultorio, id=consultorio_id)
    codigo = request.POST.get('nombre_codigo', '').strip()
    estado = request.POST.get('estado_operativo') == 'on'

    if not codigo:
        messages.error(request, "El código de consultorio es obligatorio.")
        return redirect('admin_estructura_medica')

    consultorio.nombre_codigo = codigo
    consultorio.estado_operativo = estado
    consultorio.save()

    messages.success(request, f"Consultorio '{codigo}' actualizado correctamente.")
    return redirect('admin_estructura_medica')


@login_required(login_url='login')
@require_POST
def admin_eliminar_consultorio(request, consultorio_id):
    """POST: Eliminar consultorio validando que no tenga citas asociadas."""
    if not is_admin(request.user):
        return JsonResponse({'success': False, 'error': 'Acceso denegado.'}, status=403)

    consultorio = get_object_or_404(Consultorio, id=consultorio_id)

    if Cita.objects.filter(consultorio=consultorio).exists():
        messages.error(
            request,
            f"No se puede eliminar el Consultorio '{consultorio.nombre_codigo}' porque tiene citas agendadas. Se sugiere cambiar su estado a Inactivo."
        )
    else:
        codigo = consultorio.nombre_codigo
        consultorio.delete()
        messages.success(request, f"Consultorio '{codigo}' eliminado exitosamente.")

    return redirect('admin_catalogos')


# ==========================================
# 4. GESTIÓN DE PERMISOS Y AUSENCIAS
# ==========================================
@login_required(login_url='login')
def admin_permisos_view(request):
    """Index de Solicitudes de Ausencia Médica."""
    if not is_admin(request.user):
        messages.error(request, "Acceso restringido a administradores.")
        return redirect('dashboard')

    q = request.GET.get('q', '').strip()
    estado = request.GET.get('estado', '')

    permisos_qs = AusenciasPermisos.objects.select_related('especialista__usuario', 'especialista__especialidad').all()

    if q:
        permisos_qs = permisos_qs.filter(
            Q(especialista__usuario__nombre_completo__icontains=q) |
            Q(motivo__icontains=q)
        )

    if estado and estado in EstadoAprobacion.values:
        permisos_qs = permisos_qs.filter(estado_aprobacion=estado)

    especialistas = Especialista.objects.filter(usuario__is_active=True).select_related('usuario', 'especialidad')

    context = {
        'permisos': permisos_qs.order_by('-id'),
        'especialistas': especialistas,
        'q': q,
        'estado': estado,
        'estados_aprobacion': EstadoAprobacion.choices
    }
    return render(request, 'agendamiento/admin/permisos.html', context)



@login_required(login_url='login')
@require_POST
def admin_aprobar_permiso(request, permiso_id):
    """POST: Aprobar o Rechazar solicitud de ausencia médica (HU04 / RN05)."""
    if not is_admin(request.user):
        return JsonResponse({'success': False, 'error': 'Acceso denegado.'}, status=403)

    permiso = get_object_or_404(AusenciasPermisos, id=permiso_id)
    accion = request.POST.get('accion') # 'aprobar' o 'rechazar'

    if accion == 'aprobar':
        permiso.estado_aprobacion = EstadoAprobacion.APROBADO
        permiso.save()

        # Verificar conflicto con citas agendadas (RN05)
        citas_conflicto = Cita.objects.filter(
            especialista=permiso.especialista,
            fecha_hora_inicio__gte=permiso.fecha_hora_inicio,
            fecha_hora_fin__lte=permiso.fecha_hora_fin,
            estado_cita=EstadoCita.PROGRAMADA
        )
        conflicto_cnt = citas_conflicto.count()
        citas_conflicto.update(estado_cita=EstadoCita.PENDIENTE_REUBICACION)

        if conflicto_cnt > 0:
            messages.warning(
                request,
                f"Permiso APROBADO. Se detectaron {conflicto_cnt} citas en conflicto. Marcadas como 'Pendiente de Reubicación' (Alerta RN05)."
            )
        else:
            messages.success(request, "Permiso APROBADO sin conflictos de citas.")

    elif accion == 'rechazar':
        permiso.estado_aprobacion = EstadoAprobacion.RECHAZADO
        permiso.save()
        messages.info(request, "Solicitud de permiso RECHAZADA.")

    return redirect('admin_permisos')


@login_required(login_url='login')
@require_POST
def admin_declarar_ausencia_emergencia(request):
    """POST (HU14 / RN08): Declarar Ausencia Médica de Emergencia de un Especialista para hoy."""
    if not is_admin(request.user) and request.user.rol != RolUsuario.RECEPCIONISTA:
        return JsonResponse({'success': False, 'error': 'Acceso denegado.'}, status=403)

    especialista_id = request.POST.get('especialista_id')
    if not especialista_id:
        messages.error(request, "Debes seleccionar un especialista médico.")
        return redirect('admin_permisos')

    try:
        especialista = get_object_or_404(Especialista, id=especialista_id)
        cant_afectadas, citas_list = declarar_ausencia_emergencia(especialista.id)

        messages.warning(
            request,
            f"Contingencia declarada para Dr/Dra. {especialista.usuario.nombre_completo}. "
            f"Se marcaron {cant_afectadas} citas como 'Pendiente de Reubicación' (RN08)."
        )
    except Exception as e:
        messages.error(request, f"Error al procesar la contingencia: {str(e)}")

    redirect_to = request.POST.get('redirect_to', 'admin_permisos')
    return redirect(redirect_to)


# ==========================================
# 5. APIS JSON PARA FULLCALENDAR.JS Y AJAX
# ==========================================
@login_required(login_url='login')
def api_eventos_citas(request):
    """Endpoint JSON que entrega eventos formateados para FullCalendar.js incluyendo Días Festivos (HU08)."""
    especialidad_id = request.GET.get('especialidad')
    especialista_id = request.GET.get('especialista')
    paciente_id = request.GET.get('paciente')

    citas_qs = Cita.objects.select_related('paciente__usuario', 'especialista__usuario', 'consultorio')

    # Filtrar por rol
    if request.user.rol == RolUsuario.ESPECIALISTA:
        citas_qs = citas_qs.filter(especialista__usuario=request.user)
    elif request.user.rol == RolUsuario.PACIENTE:
        citas_qs = citas_qs.filter(paciente__usuario=request.user)

    if especialidad_id:
        citas_qs = citas_qs.filter(especialista__especialidad_id=especialidad_id)
    if especialista_id:
        citas_qs = citas_qs.filter(especialista_id=especialista_id)
    if paciente_id:
        citas_qs = citas_qs.filter(paciente_id=paciente_id)


    color_map = {
        EstadoCita.PROGRAMADA: '#2C4E60',            # Primary Matte Navy
        EstadoCita.EN_SALA: '#0E6877',              # Secondary Teal
        EstadoCita.ATENDIDA: '#059669',             # Emerald
        EstadoCita.CANCELADA: '#6B7280',            # Gray
        EstadoCita.NO_ASISTIO: '#BE123C',           # Error Red
        EstadoCita.PENDIENTE_REUBICACION: '#D97706' # Amber Warning
    }

    eventos = []
    for cita in citas_qs:
        paciente_nom = cita.paciente.usuario.nombre_completo
        medico_nom = cita.especialista.usuario.nombre_completo
        consultorio_cod = cita.consultorio.nombre_codigo

        inicio_local = timezone.localtime(cita.fecha_hora_inicio)
        fin_local = timezone.localtime(cita.fecha_hora_fin)

        eventos.append({
            'id': str(cita.id),
            'title': f"{paciente_nom} - Dr. {medico_nom} (Cons. {consultorio_cod})",
            'start': inicio_local.isoformat(),
            'end': fin_local.isoformat(),
            'backgroundColor': color_map.get(cita.estado_cita, '#123748'),
            'borderColor': color_map.get(cita.estado_cita, '#123748'),
            'extendedProps': {
                'paciente': paciente_nom,
                'especialista': medico_nom,
                'especialista_id': str(cita.especialista.id),
                'especialidad_id': str(cita.especialista.especialidad.id) if cita.especialista.especialidad else '',
                'consultorio': consultorio_cod,
                'estado_cita': cita.estado_cita,
                'notas_clinicas': cita.notas_clinicas or '',
                'contador_reprogramacion': cita.contador_reprogramacion
            }
        })

    # Inyectar días festivos de Colombia como metadatos (renderizado personalizado por JS)
    year_actual = timezone.now().year
    festivos = obtener_festivos_colombia(year_actual) + obtener_festivos_colombia(year_actual + 1)
    for festivo in festivos:
        eventos.append({
            'id': f"festivo_{festivo['fecha']}",
            'title': f"🇨🇴 Festivo: {festivo['nombre']}",
            'start': festivo['fecha'],
            'display': 'none', # Ocultar renderizado nativo de evento de FullCalendar para evitar interferencias en DOM
            'extendedProps': {
                'es_festivo': True,
                'nombre_festivo': festivo['nombre']
            }
        })

    return JsonResponse(eventos, safe=False)




@login_required(login_url='login')
@require_POST
def api_actualizar_fecha_cita(request):
    """API JSON POST: Actualizar fecha/hora de cita desde arrastre en FullCalendar.js o contingencias."""
    if not is_admin(request.user) and request.user.rol != RolUsuario.RECEPCIONISTA:
        return JsonResponse({'success': False, 'error': 'Permiso denegado.'}, status=403)

    try:
        data = json.loads(request.body)
        cita_id = data.get('cita_id')
        nueva_inicio_str = data.get('nueva_fecha_inicio')
        nueva_fin_str = data.get('nueva_fecha_fin')

        cita = get_object_or_404(Cita, id=cita_id)

        inicio_dt = datetime.fromisoformat(nueva_inicio_str.replace('Z', '+00:00'))
        fin_dt = datetime.fromisoformat(nueva_fin_str.replace('Z', '+00:00'))

        cita.fecha_hora_inicio = inicio_dt
        cita.fecha_hora_fin = fin_dt
        cita.contador_reprogramacion += 1
        cita.save()

        return JsonResponse({'success': True, 'mensaje': 'Fecha de cita actualizada correctamente.'})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


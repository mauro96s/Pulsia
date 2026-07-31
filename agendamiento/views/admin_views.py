from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.core.exceptions import ValidationError

from ..models.usuarios import CustomUser, RolUsuario
from ..models.citas import Cita, EstadoCita, AusenciasPermisos, EstadoAprobacion
from ..models.especialistas import Especialidad, Consultorio, Especialista, HorarioLaboral


@login_required(login_url='login')
def admin_gestionar_ausencia_view(request, permiso_id):
    """HU04 / RN05: Aprobar o Rechazar ausencias de especialistas."""
    if request.user.rol != RolUsuario.ADMINISTRADOR:
        messages.error(request, "Acceso no autorizado.")
        return redirect('login')

    permiso = get_object_or_404(AusenciasPermisos, id=permiso_id)

    if request.method == 'POST':
        accion = request.POST.get('accion') # 'aprobar' o 'rechazar'
        if accion == 'aprobar':
            permiso.estado_aprobacion = EstadoAprobacion.APROBADO
            permiso.save()

            # RN05: Alertar si la ausencia se cruza con citas programadas
            citas_cruzadas = Cita.objects.filter(
                especialista=permiso.especialista,
                estado_cita__in=[EstadoCita.PROGRAMADA, EstadoCita.EN_SALA],
                fecha_hora_inicio__lt=permiso.fecha_hora_fin,
                fecha_hora_fin__gt=permiso.fecha_hora_inicio
            )
            count = citas_cruzadas.count()
            if count > 0:
                messages.warning(
                    request,
                    f"Ausencia APROBADA. ¡ATENCIÓN! Existen {count} citas programadas en ese intervalo que requieren reubicación en Recepción."
                )
            else:
                messages.success(request, "Ausencia APROBADA. No se encontraron cruces con citas existentes.")

        elif accion == 'rechazar':
            permiso.estado_aprobacion = EstadoAprobacion.RECHAZADO
            permiso.save()
            messages.info(request, "Solicitud de ausencia RECHAZADA.")

    return redirect('dashboard_admin')


@login_required(login_url='login')
def admin_crear_especialidad_view(request):
    """HU12: Crear nueva especialidad médica."""
    if request.user.rol != RolUsuario.ADMINISTRADOR:
        return redirect('login')

    if request.method == 'POST':
        nombre = request.POST.get('nombre_especialidad', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()

        if nombre:
            Especialidad.objects.create(nombre_especialidad=nombre, descripcion=descripcion)
            messages.success(request, f"Especialidad '{nombre}' creada correctamente.")
        else:
            messages.error(request, "El nombre de la especialidad es obligatorio.")

    return redirect('dashboard_admin')


@login_required(login_url='login')
def admin_crear_consultorio_view(request):
    """HU12: Crear nuevo consultorio."""
    if request.user.rol != RolUsuario.ADMINISTRADOR:
        return redirect('login')

    if request.method == 'POST':
        codigo = request.POST.get('nombre_codigo', '').strip()

        if codigo:
            if Consultorio.objects.filter(nombre_codigo=codigo).exists():
                messages.error(request, f"El consultorio '{codigo}' ya existe.")
            else:
                Consultorio.objects.create(nombre_codigo=codigo, estado_operativo=True)
                messages.success(request, f"Consultorio '{codigo}' creado correctamente.")
        else:
            messages.error(request, "El código del consultorio es obligatorio.")

    return redirect('dashboard_admin')


@login_required(login_url='login')
def admin_crear_empleado_view(request):
    """HU12: Crear un especialista médico con su cuenta de usuario y asignación."""
    if request.user.rol != RolUsuario.ADMINISTRADOR:
        return redirect('login')

    if request.method == 'POST':
        nombre = request.POST.get('nombre_completo', '').strip()
        correo = request.POST.get('correo', '').strip().lower()
        password = request.POST.get('password', '')
        especialidad_id = request.POST.get('especialidad_id')

        if not all([nombre, correo, password, especialidad_id]):
            messages.error(request, "Todos los campos del nuevo empleado son obligatorios.")
            return redirect('dashboard_admin')

        if CustomUser.objects.filter(correo=correo).exists():
            messages.error(request, "Ya existe un usuario con ese correo electrónico.")
            return redirect('dashboard_admin')

        try:
            user = CustomUser.objects.create_user(
                username=correo,
                correo=correo,
                email=correo,
                nombre_completo=nombre,
                rol=RolUsuario.ESPECIALISTA,
                password=password
            )
            especialidad = get_object_or_404(Especialidad, id=especialidad_id)
            especialista = Especialista.objects.create(usuario=user, especialidad=especialidad)

            # Asignar horario base de Lunes a Viernes de 8:00 a 17:00 con descanso de 12:00 a 13:00 (HU08)
            for dia in range(1, 6): # Lunes a Viernes
                HorarioLaboral.objects.create(
                    especialista=especialista,
                    dia_semana=dia,
                    hora_inicio="08:00",
                    hora_fin="17:00",
                    hora_inicio_descanso="12:00",
                    hora_fin_descanso="13:00"
                )

            messages.success(request, f"Especialista Dr/Dra. {nombre} creado exitosamente.")
        except Exception as e:
            messages.error(request, f"Error al crear especialista: {e}")

    return redirect('dashboard_admin')

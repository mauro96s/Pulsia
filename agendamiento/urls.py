from django.urls import path
from .views import (
    login_view,
    register_view,
    logout_view,
    dashboard_view,
    admin_dashboard_view,
    recepcion_dashboard_view,
    especialista_dashboard_view,
    especialista_checkin_turno_view,
    especialista_atender_cita_view,
    especialista_solicitar_permiso_view,
    paciente_dashboard_view,
    admin_usuarios_view,
    admin_crear_usuario,
    admin_editar_usuario,
    admin_eliminar_usuario,
    admin_especialistas_view,
    admin_crear_especialista,
    admin_editar_especialista,
    admin_eliminar_especialista,
    admin_estructura_medica_view,
    admin_catalogos_view,
    admin_asignaciones_view,
    admin_guardar_horario,
    admin_asignar_medico,
    admin_crear_especialidad,
    admin_editar_especialidad,
    admin_eliminar_especialidad,
    admin_crear_consultorio,
    admin_editar_consultorio,
    admin_eliminar_consultorio,
    admin_permisos_view,
    admin_aprobar_permiso,
    admin_declarar_ausencia_emergencia,
    admin_reportes_bi_view,
    admin_exportar_reporte_csv,
    api_eventos_citas,
    api_actualizar_fecha_cita,
    recepcion_checkin_medico_view,
    recepcion_anunciar_llegada_view,
    recepcion_marcar_inasistencia_view,
    recepcion_buscar_paciente_api,
    recepcion_crear_paciente_expres_view,
    recepcion_agenda_global_view,
    recepcion_agendar_reprogramar_view,
    api_horarios_disponibles_view,
    api_buscar_citas_paciente_view,
    api_especialistas_por_especialidad_view,
    recepcion_bandeja_reubicacion_view,
    recepcion_reubicar_cita_view
)

urlpatterns = [
    # Autenticación
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    
    # Dashboards principales por rol
    path('', dashboard_view, name='dashboard'),
    path('dashboard/admin/', admin_dashboard_view, name='dashboard_admin'),
    path('dashboard/recepcion/', recepcion_dashboard_view, name='dashboard_recepcion'),
    path('dashboard/especialista/', especialista_dashboard_view, name='dashboard_especialista'),
    path('especialista/checkin/', especialista_checkin_turno_view, name='especialista_checkin_turno'),
    path('especialista/cita/<int:cita_id>/atender/', especialista_atender_cita_view, name='especialista_atender_cita'),
    path('especialista/permisos/solicitar/', especialista_solicitar_permiso_view, name='especialista_solicitar_permiso'),
    path('dashboard/paciente/', paciente_dashboard_view, name='dashboard_paciente'),

    # Acciones de Recepción y Control de Citas
    path('recepcion/agenda-global/', recepcion_agenda_global_view, name='recepcion_agenda_global'),
    path('recepcion/agendar-cita/', recepcion_agendar_reprogramar_view, name='recepcion_agendar_cita'),
    path('recepcion/agendar-reprogramar/', recepcion_agendar_reprogramar_view, name='recepcion_agendar_reprogramar'),
    path('recepcion/medico/<int:especialista_id>/checkin/', recepcion_checkin_medico_view, name='recepcion_checkin_medico'),
    path('recepcion/anunciar-llegada/<int:cita_id>/', recepcion_anunciar_llegada_view, name='recepcion_anunciar_llegada'),
    path('recepcion/marcar-inasistencia/<int:cita_id>/', recepcion_marcar_inasistencia_view, name='recepcion_marcar_inasistencia'),
    path('recepcion/paciente-expres/', recepcion_crear_paciente_expres_view, name='recepcion_crear_paciente_expres'),
    path('recepcion/reubicacion/', recepcion_bandeja_reubicacion_view, name='recepcion_bandeja_reubicacion'),
    path('recepcion/reubicar/<int:cita_id>/', recepcion_reubicar_cita_view, name='recepcion_reubicar_cita'),



    # APIs JSON para Recepción
    path('api/recepcion/pacientes/buscar/', recepcion_buscar_paciente_api, name='api_buscar_pacientes'),
    path('api/recepcion/horarios-disponibles/', api_horarios_disponibles_view, name='api_horarios_disponibles'),
    path('api/recepcion/citas-paciente/', api_buscar_citas_paciente_view, name='api_citas_paciente'),
    path('api/recepcion/especialistas-especialidad/', api_especialistas_por_especialidad_view, name='api_especialistas_por_especialidad'),


    # Módulo de Administración Independiente
    path('administracion/usuarios/', admin_usuarios_view, name='admin_usuarios'),
    path('administracion/usuarios/crear/', admin_crear_usuario, name='admin_crear_usuario'),
    path('administracion/usuarios/<int:usuario_id>/editar/', admin_editar_usuario, name='admin_editar_usuario'),
    path('administracion/usuarios/<int:usuario_id>/eliminar/', admin_eliminar_usuario, name='admin_eliminar_usuario'),

    # Retrocompatibilidad para la antigua ruta especialistas
    path('administracion/especialistas/', admin_especialistas_view, name='admin_especialistas'),
    path('administracion/especialistas/crear/', admin_crear_especialista, name='admin_crear_especialista'),
    path('administracion/especialistas/<int:especialista_id>/editar/', admin_editar_especialista, name='admin_editar_especialista'),
    path('administracion/especialistas/<int:especialista_id>/eliminar/', admin_eliminar_especialista, name='admin_eliminar_especialista'),

    # Estructura Médica (Especialidades y Consultorios Físicos)
    path('administracion/estructura-medica/', admin_estructura_medica_view, name='admin_estructura_medica'),
    path('administracion/especialidades-consultorios/', admin_catalogos_view, name='admin_catalogos'),

    path('administracion/especialidad/crear/', admin_crear_especialidad, name='admin_crear_especialidad'),
    path('administracion/especialidad/<int:especialidad_id>/editar/', admin_editar_especialidad, name='admin_editar_especialidad'),
    path('administracion/especialidad/<int:especialidad_id>/eliminar/', admin_eliminar_especialidad, name='admin_eliminar_especialidad'),
    
    path('administracion/consultorio/crear/', admin_crear_consultorio, name='admin_crear_consultorio'),
    path('administracion/consultorio/<int:consultorio_id>/editar/', admin_editar_consultorio, name='admin_editar_consultorio'),
    path('administracion/consultorio/<int:consultorio_id>/eliminar/', admin_eliminar_consultorio, name='admin_eliminar_consultorio'),

    # Módulo de Asignaciones (Consultorios Físicos y Horarios Laborales de Médicos)
    path('administracion/asignaciones/', admin_asignaciones_view, name='admin_asignaciones'),
    path('administracion/estructura-medica/asignar/<int:especialista_id>/', admin_asignar_medico, name='admin_asignar_medico'),
    path('administracion/asignaciones/horarios/guardar/', admin_guardar_horario, name='admin_guardar_horario'),

    # Ausencias y Permisos
    path('administracion/permisos/', admin_permisos_view, name='admin_permisos'),
    path('administracion/permiso/<int:permiso_id>/procesar/', admin_aprobar_permiso, name='admin_aprobar_permiso'),
    path('administracion/contingencia/ausencia-emergencia/', admin_declarar_ausencia_emergencia, name='admin_declarar_ausencia_emergencia'),

    # Tablero de Reportes BI y Métricas Administrativas (HU11)
    path('administracion/reportes/', admin_reportes_bi_view, name='admin_reportes_bi'),
    path('administracion/reportes/exportar/', admin_exportar_reporte_csv, name='admin_exportar_reporte_csv'),

    # APIs JSON para FullCalendar.js y operaciones AJAX
    path('api/citas/eventos/', api_eventos_citas, name='api_eventos_citas'),
    path('api/citas/actualizar_fecha/', api_actualizar_fecha_cita, name='api_actualizar_fecha_cita'),
]



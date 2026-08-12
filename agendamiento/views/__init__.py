from .auth_views import login_view, register_view, logout_view
from .dashboard_views import (
    dashboard_view,
    recepcion_dashboard_view,
    paciente_dashboard_view
)
from .especialistas_views import (
    especialista_dashboard_view,
    especialista_checkin_turno_view,
    especialista_atender_cita_view,
    especialista_solicitar_permiso_view
)
from .admin_views import (
    admin_dashboard_view,
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
    api_eventos_citas,
    api_actualizar_fecha_cita
)
from .citas_views import (
    recepcion_dashboard_view,
    recepcion_agenda_global_view,
    recepcion_checkin_medico_view,
    recepcion_anunciar_llegada_view,
    recepcion_marcar_inasistencia_view,
    recepcion_buscar_paciente_api,
    recepcion_crear_paciente_expres_view,
    recepcion_agendar_reprogramar_view,
    api_horarios_disponibles_view,
    api_buscar_citas_paciente_view,
    api_especialistas_por_especialidad_view,
    recepcion_bandeja_reubicacion_view,
    recepcion_reubicar_cita_view
)




from .reportes_views import admin_reportes_bi_view, admin_exportar_reporte_csv

__all__ = [
    'login_view',
    'register_view',
    'logout_view',
    'dashboard_view',
    'admin_dashboard_view',
    'recepcion_dashboard_view',
    'recepcion_agenda_global_view',

    'especialista_dashboard_view',
    'especialista_checkin_turno_view',
    'especialista_atender_cita_view',
    'especialista_solicitar_permiso_view',
    'paciente_dashboard_view',
    'admin_usuarios_view',
    'admin_crear_usuario',
    'admin_editar_usuario',
    'admin_eliminar_usuario',
    'admin_especialistas_view',
    'admin_crear_especialista',
    'admin_editar_especialista',
    'admin_eliminar_especialista',
    'admin_estructura_medica_view',
    'admin_catalogos_view',
    'admin_asignaciones_view',
    'admin_guardar_horario',
    'admin_asignar_medico',
    'admin_crear_especialidad',
    'admin_editar_especialidad',
    'admin_eliminar_especialidad',
    'admin_crear_consultorio',
    'admin_editar_consultorio',
    'admin_eliminar_consultorio',
    'admin_permisos_view',
    'admin_aprobar_permiso',
    'admin_declarar_ausencia_emergencia',
    'api_eventos_citas',
    'api_actualizar_fecha_cita',
    'admin_reportes_bi_view',
    'admin_exportar_reporte_csv',
    'recepcion_anunciar_llegada_view',
    'recepcion_marcar_inasistencia_view',
    'recepcion_buscar_paciente_api',
    'recepcion_crear_paciente_expres_view',
    'recepcion_agendar_reprogramar_view',

    'api_horarios_disponibles_view',
    'api_buscar_citas_paciente_view',
    'api_especialistas_por_especialidad_view',
    'recepcion_bandeja_reubicacion_view',
    'recepcion_reubicar_cita_view'
]




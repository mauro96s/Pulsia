from .auth_views import login_view, logout_view, register_view
from .dashboard_views import (
    dashboard_view,
    admin_dashboard_view,
    recepcionista_dashboard_view,
    especialista_dashboard_view,
    paciente_dashboard_view,
)
from .paciente_views import (
    paciente_agendar_view,
    paciente_reprogramar_view,
    paciente_cancelar_view,
    paciente_unirse_espera_view,
)
from .especialista_views import (
    especialista_checkin_view,
    especialista_cambiar_estado_view,
    especialista_guardar_notas_view,
    especialista_solicitar_ausencia_view,
)
from .recepcionista_views import (
    recepcionista_agendar_view,
    recepcionista_cambiar_estado_view,
    recepcionista_reprogramar_view,
    recepcionista_contingencia_emergencia_view,
)
from .admin_views import (
    admin_gestionar_ausencia_view,
    admin_crear_especialidad_view,
    admin_crear_consultorio_view,
    admin_crear_empleado_view,
)

__all__ = [
    'login_view',
    'logout_view',
    'register_view',
    'dashboard_view',
    'admin_dashboard_view',
    'recepcionista_dashboard_view',
    'especialista_dashboard_view',
    'paciente_dashboard_view',
    'paciente_agendar_view',
    'paciente_reprogramar_view',
    'paciente_cancelar_view',
    'paciente_unirse_espera_view',
    'especialista_checkin_view',
    'especialista_cambiar_estado_view',
    'especialista_guardar_notas_view',
    'especialista_solicitar_ausencia_view',
    'recepcionista_agendar_view',
    'recepcionista_cambiar_estado_view',
    'recepcionista_reprogramar_view',
    'recepcionista_contingencia_emergencia_view',
    'admin_gestionar_ausencia_view',
    'admin_crear_especialidad_view',
    'admin_crear_consultorio_view',
    'admin_crear_empleado_view',
]

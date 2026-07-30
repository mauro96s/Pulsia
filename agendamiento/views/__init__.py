from .auth_views import login_view, logout_view, register_view
from .dashboard_views import (
    dashboard_view,
    admin_dashboard_view,
    recepcionista_dashboard_view,
    especialista_dashboard_view,
    paciente_dashboard_view,
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
]

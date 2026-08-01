from django.urls import path
from .views import (
    # Auth & Dashboards
    login_view,
    logout_view,
    register_view,
    dashboard_view,
    admin_dashboard_view,
    recepcionista_dashboard_view,
    especialista_dashboard_view,
    paciente_dashboard_view,
    paciente_agendar_cita_web_view,

    # Paciente
    paciente_agendar_view,
    paciente_reprogramar_view,
    paciente_cancelar_view,
    paciente_unirse_espera_view,

    # Especialista
    especialista_checkin_view,
    especialista_cambiar_estado_view,
    especialista_guardar_notas_view,
    especialista_solicitar_ausencia_view,

    # Recepcionista
    recepcionista_agendar_view,
    recepcionista_cambiar_estado_view,
    recepcionista_reprogramar_view,
    recepcionista_contingencia_emergencia_view,

    # Admin
    admin_gestionar_ausencia_view,
    admin_crear_especialidad_view,
    admin_crear_consultorio_view,
    admin_crear_empleado_view,
)

urlpatterns = [
    # Autenticación (HU01)
    path('login/',    login_view,    name='login'),
    path('logout/',   logout_view,   name='logout'),
    path('register/', register_view, name='register'),

    # Raíz → Redirección automática por rol
    path('', dashboard_view, name='dashboard'),

    # Dashboards por rol
    path('dashboard/admin/',          admin_dashboard_view,          name='dashboard_admin'),
    path('dashboard/recepcionista/',  recepcionista_dashboard_view,  name='dashboard_recepcionista'),
    path('dashboard/especialista/',   especialista_dashboard_view,   name='dashboard_especialista'),
    path('dashboard/paciente/',       paciente_dashboard_view,       name='dashboard_paciente'),

    # Flujo de agendamiento web
    path('paciente/agendar-cita-web/', paciente_agendar_cita_web_view, name='paciente_agendar_cita_web'),

    # Acciones Paciente
    path('paciente/agendar/',               paciente_agendar_view,       name='paciente_agendar'),
    path('paciente/reprogramar/<int:cita_id>/', paciente_reprogramar_view,   name='paciente_reprogramar'),
    path('paciente/cancelar/<int:cita_id>/',    paciente_cancelar_view,      name='paciente_cancelar'),
    path('paciente/espera/',                paciente_unirse_espera_view, name='paciente_unirse_espera'),

    # Acciones Especialista
    path('especialista/checkin/',                   especialista_checkin_view,          name='especialista_checkin'),
    path('especialista/cita/<int:cita_id>/estado/', especialista_cambiar_estado_view,   name='especialista_cambiar_estado'),
    path('especialista/cita/<int:cita_id>/notas/',  especialista_guardar_notas_view,    name='especialista_guardar_notas'),
    path('especialista/ausencia/',                  especialista_solicitar_ausencia_view, name='especialista_solicitar_ausencia'),

    # Acciones Recepcionista
    path('recepcionista/agendar/',                    recepcionista_agendar_view,                name='recepcionista_agendar'),
    path('recepcionista/cita/<int:cita_id>/estado/',  recepcionista_cambiar_estado_view,         name='recepcionista_cambiar_estado'),
    path('recepcionista/cita/<int:cita_id>/reprogramar/', recepcionista_reprogramar_view,     name='recepcionista_reprogramar'),
    path('recepcionista/contingencia/',               recepcionista_contingencia_emergencia_view, name='recepcionista_contingencia_emergencia'),

    # Acciones Admin
    path('admin/ausencia/<int:permiso_id>/gestionar/', admin_gestionar_ausencia_view, name='admin_gestionar_ausencia'),
    path('admin/especialidad/crear/',                 admin_crear_especialidad_view, name='admin_crear_especialidad'),
    path('admin/consultorio/crear/',                  admin_crear_consultorio_view,  name='admin_crear_consultorio'),
    path('admin/empleado/crear/',                     admin_crear_empleado_view,     name='admin_crear_empleado'),
]

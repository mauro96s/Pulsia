from django.urls import path
from .views import (
    login_view,
    logout_view,
    register_view,
    dashboard_view,
    admin_dashboard_view,
    recepcionista_dashboard_view,
    especialista_dashboard_view,
    paciente_dashboard_view,
)

urlpatterns = [
    # Autenticación (HU01)
    path('login/',    login_view,    name='login'),
    path('logout/',   logout_view,   name='logout'),
    path('register/', register_view, name='register'),

    # Raíz → redirige al dashboard según rol
    path('', dashboard_view, name='dashboard'),

    # Dashboards por rol
    path('dashboard/admin/',          admin_dashboard_view,          name='dashboard_admin'),
    path('dashboard/recepcionista/',  recepcionista_dashboard_view,  name='dashboard_recepcionista'),
    path('dashboard/especialista/',   especialista_dashboard_view,   name='dashboard_especialista'),
    path('dashboard/paciente/',       paciente_dashboard_view,       name='dashboard_paciente'),
]

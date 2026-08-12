from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from agendamiento.views.auth_views import redirect_by_role

@login_required(login_url='login')
def dashboard_view(request):
    """Vista principal router: Redirige automáticamente al dashboard del rol del usuario."""
    return redirect_by_role(request.user)

from agendamiento.views.admin_views import admin_dashboard_view

from agendamiento.views.citas_views import recepcion_dashboard_view

@login_required(login_url='login')
def especialista_dashboard_view(request):

    """Dashboard para el rol Especialista Médico (HU13, HU05, HU04)."""
    return render(request, 'agendamiento/dashboard/especialista.html')

@login_required(login_url='login')
def paciente_dashboard_view(request):
    """Dashboard para el rol Paciente (HU02, HU03, HU09, HU07)."""
    return render(request, 'agendamiento/dashboard/paciente.html')

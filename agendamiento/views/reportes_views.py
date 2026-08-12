import csv
import json
from datetime import datetime, timedelta, date
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone

from agendamiento.models import (
    Cita, EstadoCita, Especialidad, Especialista, Paciente, CustomUser, RolUsuario
)

def is_admin(user):
    return user.is_authenticated and (user.rol == RolUsuario.ADMINISTRADOR or user.is_superuser)

@login_required(login_url='login')
def admin_reportes_bi_view(request):
    """
    HU11: Tablero de Reportes BI y Métricas Administrativas con Gráficas y Filtros por Rango de Fechas.
    """
    if not is_admin(request.user):
        messages.error(request, "Acceso restringido únicamente a administradores.")
        return redirect('dashboard')

    # Obtener parámetros de filtro por fecha
    periodo = request.GET.get('periodo', 'mes').strip() # 'mes', 'trimestre', 'ano', 'personalizado'
    fecha_inicio_str = request.GET.get('fecha_inicio', '').strip()
    fecha_fin_str = request.GET.get('fecha_fin', '').strip()

    hoy = timezone.now().date()

    if periodo == 'trimestre':
        fecha_inicio = hoy - timedelta(days=90)
        fecha_fin = hoy
    elif periodo == 'ano':
        fecha_inicio = date(hoy.year, 1, 1)
        fecha_fin = date(hoy.year, 12, 31)
    elif periodo == 'personalizado' and fecha_inicio_str and fecha_fin_str:
        try:
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
        except ValueError:
            fecha_inicio = date(hoy.year, hoy.month, 1)
            fecha_fin = hoy
    else:
        # Por defecto: Mes Actual
        periodo = 'mes'
        fecha_inicio = date(hoy.year, hoy.month, 1)
        fecha_fin = hoy

    dt_inicio = timezone.make_aware(datetime.combine(fecha_inicio, datetime.min.time()))
    dt_fin = timezone.make_aware(datetime.combine(fecha_fin, datetime.max.time()))

    # Queryset base de citas en el rango
    citas_qs = Cita.objects.filter(fecha_hora_inicio__gte=dt_inicio, fecha_hora_inicio__lte=dt_fin)

    # 1. KPIs Globales del Período
    total_citas = citas_qs.count()
    total_atendidas = citas_qs.filter(estado_cita=EstadoCita.ATENDIDA).count()
    total_programadas = citas_qs.filter(estado_cita=EstadoCita.PROGRAMADA).count()
    total_en_sala = citas_qs.filter(estado_cita=EstadoCita.EN_SALA).count()
    total_inasistencias = citas_qs.filter(estado_cita=EstadoCita.NO_ASISTIO).count()
    total_canceladas = citas_qs.filter(estado_cita=EstadoCita.CANCELADA).count()
    total_reubicacion = citas_qs.filter(estado_cita=EstadoCita.PENDIENTE_REUBICACION).count()

    tasa_atencion = round((total_atendidas / total_citas * 100), 1) if total_citas > 0 else 0.0
    tasa_inasistencia = round((total_inasistencias / total_citas * 100), 1) if total_citas > 0 else 0.0

    # 2. Demanda por Especialidades
    especialidades = Especialidad.objects.all()
    demanda_especialidades = []
    labels_esp = []
    data_esp = []

    for esp in especialidades:
        count_citas = citas_qs.filter(especialista__especialidad=esp).count()
        demanda_especialidades.append({
            'especialidad': esp.nombre_especialidad,
            'citas_count': count_citas
        })
        if count_citas > 0:
            labels_esp.append(esp.nombre_especialidad)
            data_esp.append(count_citas)

    # Ordenar por demanda descendente
    demanda_especialidades = sorted(demanda_especialidades, key=lambda x: x['citas_count'], reverse=True)

    # 3. Datos para Gráfica de Estados de Citas
    labels_estados = ['Atendida', 'Programada', 'En Sala', 'No Asistió', 'Cancelada', 'Pend. Reubicación']
    data_estados = [
        total_atendidas,
        total_programadas,
        total_en_sala,
        total_inasistencias,
        total_canceladas,
        total_reubicacion
    ]

    # 4. Rendimiento por Especialista
    especialistas = Especialista.objects.select_related('usuario', 'especialidad').filter(usuario__is_active=True)
    desempeno_especialistas = []

    for esp in especialistas:
        citas_esp = citas_qs.filter(especialista=esp)
        cnt_tot = citas_esp.count()
        cnt_ate = citas_esp.filter(estado_cita=EstadoCita.ATENDIDA).count()
        cnt_ina = citas_esp.filter(estado_cita=EstadoCita.NO_ASISTIO).count()
        cnt_can = citas_esp.filter(estado_cita=EstadoCita.CANCELADA).count()

        tasa_ina_esp = round((cnt_ina / cnt_tot * 100), 1) if cnt_tot > 0 else 0.0

        desempeno_especialistas.append({
            'especialista': esp,
            'total': cnt_tot,
            'atendidas': cnt_ate,
            'inasistencias': cnt_ina,
            'canceladas': cnt_can,
            'tasa_inasistencia': tasa_ina_esp
        })

    context = {
        'periodo': periodo,
        'fecha_inicio': fecha_inicio.strftime('%Y-%m-%d'),
        'fecha_fin': fecha_fin.strftime('%Y-%m-%d'),
        'total_citas': total_citas,
        'total_atendidas': total_atendidas,
        'total_programadas': total_programadas,
        'total_en_sala': total_en_sala,
        'total_inasistencias': total_inasistencias,
        'total_canceladas': total_canceladas,
        'total_reubicacion': total_reubicacion,
        'tasa_atencion': tasa_atencion,
        'tasa_inasistencia': tasa_inasistencia,
        'demanda_especialidades': demanda_especialidades,
        'desempeno_especialistas': desempeno_especialistas,
        # JSON preparado para Chart.js
        'chart_esp_labels_json': json.dumps(labels_esp),
        'chart_esp_data_json': json.dumps(data_esp),
        'chart_est_labels_json': json.dumps(labels_estados),
        'chart_est_data_json': json.dumps(data_estados),
    }

    return render(request, 'agendamiento/reportes/reportes_bi.html', context)


@login_required(login_url='login')
def admin_exportar_reporte_csv(request):
    """
    Exporta el informe consolidado de citas y rendimiento por especialista en formato CSV.
    """
    if not is_admin(request.user):
        return HttpResponse("Acceso no autorizado", status=403)

    fecha_inicio_str = request.GET.get('fecha_inicio', '').strip()
    fecha_fin_str = request.GET.get('fecha_fin', '').strip()

    hoy = timezone.now().date()

    try:
        dt_inicio = timezone.make_aware(datetime.combine(datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date(), datetime.min.time()))
        dt_fin = timezone.make_aware(datetime.combine(datetime.strptime(fecha_fin_str, '%Y-%m-%d').date(), datetime.max.time()))
    except (ValueError, TypeError):
        dt_inicio = timezone.make_aware(datetime.combine(date(hoy.year, hoy.month, 1), datetime.min.time()))
        dt_fin = timezone.make_aware(datetime.combine(hoy, datetime.max.time()))

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="reporte_pulsia_bi_{hoy.strftime("%Y%m%d")}.csv"'

    writer = csv.writer(response)
    # Encabezado CSV
    writer.writerow(['REPORTE ADMINISTRATIVO DE RENDIMIENTO MÉDICO Y CITAS - PULSIA'])
    writer.writerow([f'Período Evaluado: {dt_inicio.strftime("%Y-%m-%d")} a {dt_fin.strftime("%Y-%m-%d")}'])
    writer.writerow([])
    writer.writerow(['Especialista', 'Especialidad', 'Consultorio', 'Total Citas', 'Atendidas', 'No Asistió', 'Canceladas', 'Tasa Inasistencia (%)'])

    especialistas = Especialista.objects.select_related('usuario', 'especialidad', 'consultorio').filter(usuario__is_active=True)
    citas_qs = Cita.objects.filter(fecha_hora_inicio__gte=dt_inicio, fecha_hora_inicio__lte=dt_fin)

    for esp in especialistas:
        citas_esp = citas_qs.filter(especialista=esp)
        cnt_tot = citas_esp.count()
        cnt_ate = citas_esp.filter(estado_cita=EstadoCita.ATENDIDA).count()
        cnt_ina = citas_esp.filter(estado_cita=EstadoCita.NO_ASISTIO).count()
        cnt_can = citas_esp.filter(estado_cita=EstadoCita.CANCELADA).count()

        tasa_ina_esp = round((cnt_ina / cnt_tot * 100), 1) if cnt_tot > 0 else 0.0

        writer.writerow([
            esp.usuario.nombre_completo,
            esp.especialidad.nombre_especialidad if esp.especialidad else 'N/A',
            esp.consultorio.nombre_codigo if esp.consultorio else 'N/A',
            cnt_tot,
            cnt_ate,
            cnt_ina,
            cnt_can,
            f"{tasa_ina_esp}%"
        ])

    return response

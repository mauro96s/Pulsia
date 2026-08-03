import os
import django
from datetime import datetime, timedelta, time
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from agendamiento.models.usuarios import CustomUser, RolUsuario
from agendamiento.models.especialistas import Especialidad, Consultorio, Especialista, HorarioLaboral, EstadoTurno
from agendamiento.models.pacientes import Paciente
from agendamiento.models.citas import Cita, EstadoCita, AusenciasPermisos, EstadoAprobacion, ListaEspera

def run_seed():
    print("[*] Iniciando la siembra de datos de prueba en Pulsia...")

    # 1. ESPECIALIDADES
    especialidades_data = [
        ("Medicina General", "Atención primaria, diagnósticos iniciales y chequeos preventivos."),
        ("Cardiología", "Prevención, diagnóstico y tratamiento de enfermedades cardiovasculares."),
        ("Pediatría", "Atención médica integral para lactantes, niños y adolescentes."),
        ("Dermatología", "Diagnóstico y tratamiento de patologías de la piel, cabello y uñas."),
        ("Oftalmología", "Salud visual, corrección refractiva y tratamiento de enfermedades oculares."),
        ("Ortopedia y Traumatología", "Tratamiento de lesiones musculoesqueléticas, fracturas y articulaciones."),
        ("Ginecología y Obstetricia", "Salud reproductiva femenina y seguimiento del embarazo.")
    ]

    especialidades_dict = {}
    for nombre, desc in especialidades_data:
        esp, _ = Especialidad.objects.get_or_create(
            nombre_especialidad=nombre,
            defaults={'descripcion': desc}
        )
        especialidades_dict[nombre] = esp
    print(f"[OK] {len(especialidades_dict)} Especialidades listas.")

    # 2. CONSULTORIOS
    consultorios_codes = ["101", "102", "201", "202", "301", "302"]
    consultorios_dict = {}
    for code in consultorios_codes:
        c, _ = Consultorio.objects.get_or_create(
            nombre_codigo=code,
            defaults={'estado_operativo': True}
        )
        consultorios_dict[code] = c
    print(f"[OK] {len(consultorios_dict)} Consultorios listos.")

    # 3. USUARIOS Y ROLES
    # Admin
    admin_user, _ = CustomUser.objects.get_or_create(
        correo="admin@pulsia.com",
        defaults={
            'username': "admin@pulsia.com",
            'nombre_completo': "Carlos Mendoza",
            'rol': RolUsuario.ADMINISTRADOR,
            'telefono': "+57 300 123 4567",
            'estado_cuenta': True
        }
    )
    admin_user.set_password("admin123")
    admin_user.save()

    # Recepcionistas
    rec_user1, _ = CustomUser.objects.get_or_create(
        correo="recepcion@pulsia.com",
        defaults={
            'username': "recepcion@pulsia.com",
            'nombre_completo': "Laura Rodriguez",
            'rol': RolUsuario.RECEPCIONISTA,
            'telefono': "+57 310 987 6543",
            'estado_cuenta': True
        }
    )
    rec_user1.set_password("recepcion123")
    rec_user1.save()

    rec_user2, _ = CustomUser.objects.get_or_create(
        correo="recepcion2@pulsia.com",
        defaults={
            'username': "recepcion2@pulsia.com",
            'nombre_completo': "Andrea Gomez",
            'rol': RolUsuario.RECEPCIONISTA,
            'telefono': "+57 312 456 7890",
            'estado_cuenta': True
        }
    )
    rec_user2.set_password("recepcion123")
    rec_user2.save()

    print("[OK] Usuarios Administrador y Recepcionistas creados.")

    # Especialistas
    especialistas_list_data = [
        ("cardiologia@pulsia.com", "Dr. Roberto Gomez", "Cardiología", EstadoTurno.PRESENTE),
        ("pediatria@pulsia.com", "Dra. Ana Maria Martinez", "Pediatría", EstadoTurno.PRESENTE),
        ("general@pulsia.com", "Dr. Juan Pablo Vargas", "Medicina General", EstadoTurno.PRESENTE),
        ("dermatologia@pulsia.com", "Dra. Sofia Ramirez", "Dermatología", EstadoTurno.AUSENTE),
        ("oftalmologia@pulsia.com", "Dr. Camilo Torres", "Oftalmología", EstadoTurno.PRESENTE),
        ("ortopedia@pulsia.com", "Dr. Felipe Mendoza", "Ortopedia y Traumatología", EstadoTurno.AUSENTE)
    ]

    especialistas_obj_list = []
    for email, nombre, esp_nombre, turno in especialistas_list_data:
        usr, _ = CustomUser.objects.get_or_create(
            correo=email,
            defaults={
                'username': email,
                'nombre_completo': nombre,
                'rol': RolUsuario.ESPECIALISTA,
                'telefono': "+57 301 555 0199",
                'estado_cuenta': True
            }
        )
        usr.set_password("medico123")
        usr.save()

        esp, _ = Especialista.objects.get_or_create(
            usuario=usr,
            defaults={
                'especialidad': especialidades_dict[esp_nombre],
                'estado_turno': turno
            }
        )
        especialistas_obj_list.append(esp)

        # Horarios laborales (Lunes a Viernes 08:00 a 17:00, Descanso 12:00 a 14:00)
        for dia in range(1, 6):
            HorarioLaboral.objects.get_or_create(
                especialista=esp,
                dia_semana=dia,
                defaults={
                    'hora_inicio': time(8, 0),
                    'hora_fin': time(17, 0),
                    'hora_inicio_descanso': time(12, 0),
                    'hora_fin_descanso': time(14, 0)
                }
            )

    print(f"[OK] {len(especialistas_obj_list)} Medicos Especialistas y Horarios creados.")

    # Pacientes
    pacientes_data = [
        ("paciente1@pulsia.com", "Maria Fernanda Lopez", "+57 315 111 2233", datetime(1994, 5, 12).date(), 0),
        ("paciente2@pulsia.com", "Alejandro Morales", "+57 318 444 5566", datetime(1988, 11, 23).date(), 1),
        ("paciente3@pulsia.com", "Mateo Gutierrez", "+57 300 777 8899", datetime(2001, 3, 4).date(), 0),
        ("paciente4@pulsia.com", "Valentina Castro", "+57 312 999 0011", datetime(1996, 9, 18).date(), 3) # Penalizado (RN04)
    ]

    pacientes_obj_list = []
    for email, nombre, tel, fecha_nac, inasistencias in pacientes_data:
        usr, _ = CustomUser.objects.get_or_create(
            correo=email,
            defaults={
                'username': email,
                'nombre_completo': nombre,
                'rol': RolUsuario.PACIENTE,
                'telefono': tel,
                'estado_cuenta': True
            }
        )
        usr.set_password("paciente123")
        usr.save()

        p, _ = Paciente.objects.get_or_create(
            usuario=usr,
            defaults={
                'fecha_nacimiento': fecha_nac,
                'acepta_habeas_data': True,
                'contador_inasistencias': inasistencias
            }
        )
        pacientes_obj_list.append(p)

    print(f"[OK] {len(pacientes_obj_list)} Pacientes creados.")

    # 4. CITAS MÉDICAS DE PRUEBA
    hoy = timezone.now()
    hoy_date = hoy.date()

    p_maria = pacientes_obj_list[0]
    p_alejandro = pacientes_obj_list[1]
    p_mateo = pacientes_obj_list[2]
    p_valentina = pacientes_obj_list[3]

    esp_cardio = especialistas_obj_list[0]
    esp_pedia = especialistas_obj_list[1]
    esp_general = especialistas_obj_list[2]
    esp_derma = especialistas_obj_list[3]
    esp_oftalmo = especialistas_obj_list[4]

    c_101 = consultorios_dict["101"]
    c_102 = consultorios_dict["102"]
    c_201 = consultorios_dict["201"]
    c_202 = consultorios_dict["202"]

    # Citas pasadas atendidas (con notas clínicas)
    Cita.objects.get_or_create(
        paciente=p_maria,
        especialista=esp_cardio,
        fecha_hora_inicio=timezone.make_aware(datetime.combine(hoy_date - timedelta(days=5), time(9, 0))),
        defaults={
            'consultorio': c_101,
            'fecha_hora_fin': timezone.make_aware(datetime.combine(hoy_date - timedelta(days=5), time(9, 30))),
            'estado_cita': EstadoCita.ATENDIDA,
            'notas_clinicas': "Paciente presenta presion arterial 120/80 mmHg. Electrocardiograma normal. Se recomienda continuar con dieta baja en sodio y control en 6 meses."
        }
    )

    Cita.objects.get_or_create(
        paciente=p_alejandro,
        especialista=esp_general,
        fecha_hora_inicio=timezone.make_aware(datetime.combine(hoy_date - timedelta(days=3), time(10, 0))),
        defaults={
            'consultorio': c_201,
            'fecha_hora_fin': timezone.make_aware(datetime.combine(hoy_date - timedelta(days=3), time(10, 30))),
            'estado_cita': EstadoCita.ATENDIDA,
            'notas_clinicas': "Chequeo medico de rutina. Examenes de laboratorio en rangos normales. Se prescribe suplementacion con Vitamina D."
        }
    )

    # Citas para hoy (en diferentes estados)
    Cita.objects.get_or_create(
        paciente=p_maria,
        especialista=esp_cardio,
        fecha_hora_inicio=timezone.make_aware(datetime.combine(hoy_date, time(8, 30))),
        defaults={
            'consultorio': c_101,
            'fecha_hora_fin': timezone.make_aware(datetime.combine(hoy_date, time(9, 0))),
            'estado_cita': EstadoCita.EN_SALA
        }
    )

    Cita.objects.get_or_create(
        paciente=p_alejandro,
        especialista=esp_pedia,
        fecha_hora_inicio=timezone.make_aware(datetime.combine(hoy_date, time(9, 30))),
        defaults={
            'consultorio': c_102,
            'fecha_hora_fin': timezone.make_aware(datetime.combine(hoy_date, time(10, 0))),
            'estado_cita': EstadoCita.PROGRAMADA
        }
    )

    Cita.objects.get_or_create(
        paciente=p_mateo,
        especialista=esp_oftalmo,
        fecha_hora_inicio=timezone.make_aware(datetime.combine(hoy_date, time(10, 30))),
        defaults={
            'consultorio': c_202,
            'fecha_hora_fin': timezone.make_aware(datetime.combine(hoy_date, time(11, 0))),
            'estado_cita': EstadoCita.PROGRAMADA
        }
    )

    Cita.objects.get_or_create(
        paciente=p_valentina,
        especialista=esp_derma,
        fecha_hora_inicio=timezone.make_aware(datetime.combine(hoy_date, time(14, 15))),
        defaults={
            'consultorio': c_201,
            'fecha_hora_fin': timezone.make_aware(datetime.combine(hoy_date, time(14, 45))),
            'estado_cita': EstadoCita.PENDIENTE_REUBICACION
        }
    )

    # Citas futuras
    for i in range(1, 4):
        dia_futuro = hoy_date + timedelta(days=i)
        Cita.objects.get_or_create(
            paciente=p_maria,
            especialista=esp_cardio,
            fecha_hora_inicio=timezone.make_aware(datetime.combine(dia_futuro, time(10, 0))),
            defaults={
                'consultorio': c_101,
                'fecha_hora_fin': timezone.make_aware(datetime.combine(dia_futuro, time(10, 30))),
                'estado_cita': EstadoCita.PROGRAMADA
            }
        )

        Cita.objects.get_or_create(
            paciente=p_mateo,
            especialista=esp_general,
            fecha_hora_inicio=timezone.make_aware(datetime.combine(dia_futuro, time(15, 15))),
            defaults={
                'consultorio': c_201,
                'fecha_hora_fin': timezone.make_aware(datetime.combine(dia_futuro, time(15, 45))),
                'estado_cita': EstadoCita.PROGRAMADA
            }
        )

    print("[OK] Citas medicas pasadas, de hoy y futuras creadas.")

    # 5. PERMISOS Y AUSENCIAS
    esp_ortopedia = especialistas_obj_list[5]
    AusenciasPermisos.objects.get_or_create(
        especialista=esp_ortopedia,
        fecha_hora_inicio=timezone.make_aware(datetime.combine(hoy_date + timedelta(days=1), time(8, 0))),
        defaults={
            'fecha_hora_fin': timezone.make_aware(datetime.combine(hoy_date + timedelta(days=1), time(17, 0))),
            'motivo_solicitud': "Calamidad medica familiar no programada",
            'estado_aprobacion': EstadoAprobacion.PENDIENTE
        }
    )

    AusenciasPermisos.objects.get_or_create(
        especialista=esp_derma,
        fecha_hora_inicio=timezone.make_aware(datetime.combine(hoy_date, time(8, 0))),
        defaults={
            'fecha_hora_fin': timezone.make_aware(datetime.combine(hoy_date, time(17, 0))),
            'motivo_solicitud': "Asistencia a simposio internacional de dermatologia clinica",
            'estado_aprobacion': EstadoAprobacion.APROBADO
        }
    )
    print("[OK] Permisos y solicitudes de ausencias medicas creadas.")

    # 6. LISTA DE ESPERA
    ListaEspera.objects.get_or_create(
        paciente=p_alejandro,
        especialista=esp_cardio,
        defaults={
            'especialidad': especialidades_dict["Cardiología"],
            'fecha_solicitada': hoy_date + timedelta(days=2),
            'estado': 'Pendiente'
        }
    )
    print("[OK] Registros de lista de espera creados.")

    print("\n[OK] PROCESO DE POBLACION DE DATOS COMPLETADO CON EXITO!")
    print("-------------------------------------------------------")
    print("Credenciales de Prueba Disponibles:")
    print(" * Administrador:  admin@pulsia.com       | Contrasena: admin123")
    print(" * Recepcionista:  recepcion@pulsia.com   | Contrasena: recepcion123")
    print(" * Especialista:   cardiologia@pulsia.com | Contrasena: medico123")
    print(" * Paciente Frec:  paciente1@pulsia.com   | Contrasena: paciente123")
    print(" * Pac. Penaliz:   paciente4@pulsia.com   | Contrasena: paciente123")
    print("-------------------------------------------------------")

if __name__ == '__main__':
    run_seed()

import datetime
from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError

from agendamiento.models import (
    CustomUser, RolUsuario, Paciente, Especialidad,
    Consultorio, Especialista, EstadoTurno, Cita,
    EstadoCita, AusenciasPermisos, EstadoAprobacion
)
from agendamiento.services.citas_service import (
    agendar_cita_web,
    reprogramar_cita,
    cancelar_cita,
    registrar_inasistencia,
    registrar_notas_clinicas,
    activar_contingencia_emergencia
)


class ReglasNegocioTestCase(TestCase):
    def setUp(self):
        # Crear usuarios y perfiles
        self.user_paciente = CustomUser.objects.create_user(
            username='paciente@pulsia.com',
            correo='paciente@pulsia.com',
            nombre_completo='Paciente Test',
            rol=RolUsuario.PACIENTE,
            password='Password123!'
        )
        self.paciente = Paciente.objects.create(
            usuario=self.user_paciente,
            fecha_nacimiento='1995-01-01',
            acepta_habeas_data=True
        )

        self.user_medico = CustomUser.objects.create_user(
            username='medico@pulsia.com',
            correo='medico@pulsia.com',
            nombre_completo='Doctor Test',
            rol=RolUsuario.ESPECIALISTA,
            password='Password123!'
        )
        self.especialidad = Especialidad.objects.create(
            nombre_especialidad='Medicina General'
        )
        self.especialista = Especialista.objects.create(
            usuario=self.user_medico,
            especialidad=self.especialidad
        )

        self.consultorio = Consultorio.objects.create(
            nombre_codigo='101'
        )

    def test_rn04_bloqueo_por_inasistencias(self):
        """RN04: 3 inasistencias bloquean agendamiento web."""
        self.paciente.contador_inasistencias = 3
        self.paciente.save()

        fecha_futura = timezone.now() + datetime.timedelta(days=2)

        with self.assertRaises(ValidationError) as ctx:
            agendar_cita_web(
                paciente=self.paciente,
                especialista=self.especialista,
                consultorio=self.consultorio,
                fecha_hora_inicio=fecha_futura
            )
        self.assertIn("bloqueado", str(ctx.exception))

    def test_rn01_rn02_reprogramacion_web(self):
        """RN01 y RN02: Validación de 24h y máximo 1 reprogramación web."""
        fecha_futura = timezone.now() + datetime.timedelta(days=3)
        cita = Cita.objects.create(
            paciente=self.paciente,
            especialista=self.especialista,
            consultorio=self.consultorio,
            fecha_hora_inicio=fecha_futura,
            fecha_hora_fin=fecha_futura + datetime.timedelta(minutes=30),
            estado_cita=EstadoCita.PROGRAMADA
        )

        # 1. Reprogramar exitosamente por 1ra vez a >24h
        nueva_fecha_1 = fecha_futura + datetime.timedelta(days=1)
        reprogramar_cita(cita, nueva_fecha_1, es_recepcion=False)
        self.assertEqual(cita.contador_reprogramacion, 1)

        # 2. Reintento web (RN01: debe fallar por contador >= 1)
        nueva_fecha_2 = fecha_futura + datetime.timedelta(days=2)
        with self.assertRaises(ValidationError) as ctx:
            reprogramar_cita(cita, nueva_fecha_2, es_recepcion=False)
        self.assertIn("RN01", str(ctx.exception))

    def test_rn06_privacidad_y_estado_notas_clinicas(self):
        """RN06 & HU05: Solo se agregan notas si la cita está en estado Atendida."""
        fecha_futura = timezone.now() + datetime.timedelta(days=1)
        cita = Cita.objects.create(
            paciente=self.paciente,
            especialista=self.especialista,
            consultorio=self.consultorio,
            fecha_hora_inicio=fecha_futura,
            fecha_hora_fin=fecha_futura + datetime.timedelta(minutes=30),
            estado_cita=EstadoCita.PROGRAMADA
        )

        # Debe fallar mientras esté Programada
        with self.assertRaises(ValidationError):
            registrar_notas_clinicas(cita, self.user_medico, "Paciente estable.")

        # Cambiar a Atendida y registrar notas
        cita.estado_cita = EstadoCita.ATENDIDA
        cita.save()

        registrar_notas_clinicas(cita, self.user_medico, "Paciente en excelente estado.")
        cita.refresh_from_db()
        self.assertEqual(cita.notas_clinicas, "Paciente en excelente estado.")

    def test_hu14_rn08_contingencia_emergencia(self):
        """HU14 & RN08: Contingencia por ausencia de emergencia del especialista."""
        hoy = timezone.now()
        cita = Cita.objects.create(
            paciente=self.paciente,
            especialista=self.especialista,
            consultorio=self.consultorio,
            fecha_hora_inicio=hoy + datetime.timedelta(hours=2),
            fecha_hora_fin=hoy + datetime.timedelta(hours=2, minutes=30),
            estado_cita=EstadoCita.PROGRAMADA
        )

        citas_afectadas = activar_contingencia_emergencia(self.especialista, None)
        self.assertEqual(len(citas_afectadas), 1)

        cita.refresh_from_db()
        self.assertEqual(cita.estado_cita, EstadoCita.PENDIENTE_REUBICACION)

        self.especialista.refresh_from_db()
        self.assertEqual(self.especialista.estado_turno, EstadoTurno.AUSENTE)

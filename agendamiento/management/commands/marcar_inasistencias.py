from django.core.management.base import BaseCommand
from django.utils import timezone
import datetime
from agendamiento.models.citas import Cita, EstadoCita

class Command(BaseCommand):
    help = 'Marca automáticamente las citas como No Asistió si pasan más de 15 minutos (RN03)'

    def handle(self, *args, **kwargs):
        ahora = timezone.now()
        limite_tolerancia = ahora - datetime.timedelta(minutes=15)

        # Buscar citas PROGRAMADAS cuya hora de inicio ya pasó hace más de 15 minutos
        citas_atrasadas = Cita.objects.filter(
            estado_cita=EstadoCita.PROGRAMADA,
            fecha_hora_inicio__lt=limite_tolerancia
        )

        marcadas = 0
        for cita in citas_atrasadas:
            cita.estado_cita = EstadoCita.NO_ASISTIO
            cita.save()
            
            # Penalización RN04: Sumar 1 al contador
            paciente = cita.paciente
            if paciente:
                paciente.contador_inasistencias += 1
                paciente.save()
            marcadas += 1

        if marcadas > 0:
            self.stdout.write(self.style.SUCCESS(f'Se marcaron {marcadas} citas como NO_ASISTIO por superar el límite de 15 minutos.'))
        else:
            self.stdout.write(self.style.SUCCESS('No se encontraron citas atrasadas.'))

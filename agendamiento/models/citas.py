from django.db import models
from .pacientes import Paciente
from .especialistas import Especialista, Consultorio

class EstadoCita(models.TextChoices):
    PROGRAMADA = 'Programada', 'Programada'
    EN_SALA = 'En_Sala', 'En Sala'
    ATENDIDA = 'Atendida', 'Atendida'
    CANCELADA = 'Cancelada', 'Cancelada'
    NO_ASISTIO = 'No_Asistio', 'No Asistió'
    PENDIENTE_REUBICACION = 'Pendiente_Reubicacion', 'Pendiente de Reubicación'

class Cita(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='citas')
    especialista = models.ForeignKey(Especialista, on_delete=models.CASCADE, related_name='citas')
    consultorio = models.ForeignKey(Consultorio, on_delete=models.RESTRICT)
    
    fecha_hora_inicio = models.DateTimeField()
    fecha_hora_fin = models.DateTimeField()
    estado_cita = models.CharField(
        max_length=30, 
        choices=EstadoCita.choices, 
        default=EstadoCita.PROGRAMADA
    )
    contador_reprogramacion = models.IntegerField(default=0)
    notas_clinicas = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Cita {self.id}: {self.paciente.usuario.nombre_completo} con {self.especialista}"

class EstadoAprobacion(models.TextChoices):
    PENDIENTE = 'Pendiente', 'Pendiente'
    APROBADO = 'Aprobado', 'Aprobado'
    RECHAZADO = 'Rechazado', 'Rechazado'

class AusenciasPermisos(models.Model):
    especialista = models.ForeignKey(Especialista, on_delete=models.CASCADE, related_name='permisos')
    fecha_hora_inicio = models.DateTimeField()
    fecha_hora_fin = models.DateTimeField()
    motivo_solicitud = models.TextField()
    estado_aprobacion = models.CharField(
        max_length=20, 
        choices=EstadoAprobacion.choices, 
        default=EstadoAprobacion.PENDIENTE
    )

    def __str__(self):
        return f"Permiso {self.estado_aprobacion} - {self.especialista}"

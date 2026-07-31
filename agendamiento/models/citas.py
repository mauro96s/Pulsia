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

    class Meta:
        app_label = 'agendamiento'

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

    class Meta:
        app_label = 'agendamiento'

    def __str__(self):
        return f"Permiso {self.estado_aprobacion} - {self.especialista}"

class EstadoListaEspera(models.TextChoices):
    PENDIENTE = 'Pendiente', 'Pendiente'
    NOTIFICADO = 'Notificado', 'Notificado'
    ATENDIDO = 'Atendido', 'Atendido'
    CANCELADO = 'Cancelado', 'Cancelado'

class ListaEspera(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='listas_espera')
    especialista = models.ForeignKey(Especialista, on_delete=models.CASCADE, related_name='listas_espera', null=True, blank=True)
    especialidad = models.ForeignKey('Especialidad', on_delete=models.CASCADE, related_name='listas_espera', null=True, blank=True)
    fecha_solicitada = models.DateField(null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=EstadoListaEspera.choices, default=EstadoListaEspera.PENDIENTE)

    class Meta:
        app_label = 'agendamiento'

    def __str__(self):
        return f"Lista Espera: {self.paciente.usuario.nombre_completo} ({self.estado})"


from django.db import models
from django.conf import settings

class Especialidad(models.Model):
    nombre_especialidad = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre_especialidad

class Consultorio(models.Model):
    nombre_codigo = models.CharField(max_length=50, unique=True)
    estado_operativo = models.BooleanField(default=True)

    def __str__(self):
        return f"Consultorio {self.nombre_codigo}"

class EstadoTurno(models.TextChoices):
    PRESENTE = 'Presente', 'Presente'
    AUSENTE = 'Ausente', 'Ausente'

class Especialista(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='perfil_especialista'
    )
    especialidad = models.ForeignKey(
        Especialidad, 
        on_delete=models.RESTRICT,
        related_name='especialistas'
    )
    estado_turno = models.CharField(
        max_length=20, 
        choices=EstadoTurno.choices, 
        default=EstadoTurno.AUSENTE
    )

    def __str__(self):
        return f"Dr/Dra. {self.usuario.nombre_completo} - {self.especialidad.nombre_especialidad}"

class HorarioLaboral(models.Model):
    especialista = models.ForeignKey(Especialista, on_delete=models.CASCADE, related_name='horarios')
    dia_semana = models.IntegerField(choices=[
        (1, 'Lunes'), (2, 'Martes'), (3, 'Miércoles'),
        (4, 'Jueves'), (5, 'Viernes'), (6, 'Sábado'), (7, 'Domingo')
    ])
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    hora_inicio_descanso = models.TimeField(blank=True, null=True)
    hora_fin_descanso = models.TimeField(blank=True, null=True)

    class Meta:
        unique_together = ('especialista', 'dia_semana')

    def __str__(self):
        return f"{self.especialista} - Día {self.dia_semana} ({self.hora_inicio} a {self.hora_fin})"

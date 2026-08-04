from django.db import models
from django.conf import settings

class Especialidad(models.Model):
    nombre_especialidad = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        app_label = 'agendamiento'

    def __str__(self):
        return self.nombre_especialidad

class Consultorio(models.Model):
    nombre_codigo = models.CharField(max_length=50, unique=True)
    estado_operativo = models.BooleanField(default=True)

    class Meta:
        app_label = 'agendamiento'

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
    consultorio_asignado = models.ForeignKey(
        Consultorio,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='especialistas'
    )

    class Meta:
        app_label = 'agendamiento'

    def __str__(self):
        return f"Dr/Dra. {self.usuario.nombre_completo} - {self.especialidad.nombre_especialidad}"

from datetime import datetime
from django.core.exceptions import ValidationError

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
        app_label = 'agendamiento'
        unique_together = ('especialista', 'dia_semana')

    def clean(self):
        super().clean()
        if self.hora_inicio and self.hora_fin:
            dt1 = datetime.combine(datetime.min, self.hora_inicio)
            dt2 = datetime.combine(datetime.min, self.hora_fin)
            if dt2 <= dt1:
                raise ValidationError("La hora de fin debe ser posterior a la hora de inicio.")
            
            duracion_segundos = (dt2 - dt1).total_seconds()
            if self.hora_inicio_descanso and self.hora_fin_descanso:
                dt_desc1 = datetime.combine(datetime.min, self.hora_inicio_descanso)
                dt_desc2 = datetime.combine(datetime.min, self.hora_fin_descanso)
                if dt_desc2 > dt_desc1:
                    duracion_segundos -= (dt_desc2 - dt_desc1).total_seconds()

            horas_trabajo = duracion_segundos / 3600.0
            if horas_trabajo > 6.0:
                raise ValidationError("Un especialista no puede trabajar más de 6 horas diarias en su jornada.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.especialista} - Día {self.dia_semana} ({self.hora_inicio} a {self.hora_fin})"

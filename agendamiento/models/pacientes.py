from django.db import models
from .usuarios import CustomUser

class Paciente(models.Model):
    usuario = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='perfil_paciente')
    fecha_nacimiento = models.DateField()
    acepta_habeas_data = models.BooleanField(default=False)
    contador_inasistencias = models.IntegerField(default=0)

    class Meta:
        app_label = 'agendamiento'

    def __str__(self):
        return f"Paciente: {self.usuario.nombre_completo}"

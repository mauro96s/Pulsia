from django.contrib.auth.models import AbstractUser
from django.db import models

class RolUsuario(models.TextChoices):
    ADMINISTRADOR = 'Administrador', 'Administrador'
    RECEPCIONISTA = 'Recepcionista', 'Recepcionista'
    ESPECIALISTA = 'Especialista', 'Especialista'
    PACIENTE = 'Paciente', 'Paciente'

class CustomUser(AbstractUser):
    nombre_completo = models.CharField(max_length=150)
    correo = models.EmailField(unique=True)
    rol = models.CharField(max_length=20, choices=RolUsuario.choices)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    estado_cuenta = models.BooleanField(default=True)

    USERNAME_FIELD = 'correo'
    REQUIRED_FIELDS = ['username', 'nombre_completo', 'rol']

    def __str__(self):
        return f"{self.nombre_completo} ({self.rol})"

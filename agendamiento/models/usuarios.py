from django.contrib.auth.models import AbstractUser
from django.db import models

class RolUsuario(models.TextChoices):
    ADMINISTRADOR = 'Administrador', 'Administrador'
    RECEPCIONISTA = 'Recepcionista', 'Recepcionista'
    ESPECIALISTA = 'Especialista', 'Especialista'
    PACIENTE = 'Paciente', 'Paciente'

class TipoDocumento(models.TextChoices):
    CC = 'CC', 'Cédula de Ciudadanía'
    CE = 'CE', 'Cédula de Extranjería'
    TI = 'TI', 'Tarjeta de Identidad'
    RC = 'RC', 'Registro Civil'
    PA = 'PA', 'Pasaporte'

class CustomUser(AbstractUser):
    nombre_completo = models.CharField(max_length=150)
    tipo_documento = models.CharField(
        max_length=10, 
        choices=TipoDocumento.choices, 
        default=TipoDocumento.CC,
        blank=True, 
        null=True
    )
    num_documento = models.CharField(
        max_length=30, 
        unique=True, 
        blank=True, 
        null=True
    )
    correo = models.EmailField(unique=True)
    rol = models.CharField(max_length=20, choices=RolUsuario.choices)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    estado_cuenta = models.BooleanField(default=True)

    USERNAME_FIELD = 'correo'
    REQUIRED_FIELDS = ['username', 'nombre_completo', 'rol']

    def __str__(self):
        return f"{self.nombre_completo} ({self.tipo_documento or ''} {self.num_documento or ''}) - {self.rol}"

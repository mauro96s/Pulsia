from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, Paciente, Especialidad, Consultorio, 
    Especialista, HorarioLaboral, Cita, AusenciasPermisos
)

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('correo', 'nombre_completo', 'rol', 'estado_cuenta', 'is_staff')
    list_filter = ('rol', 'estado_cuenta', 'is_staff')
    search_fields = ('correo', 'nombre_completo')
    ordering = ('correo',)
    fieldsets = UserAdmin.fieldsets + (
        ('Información Adicional', {'fields': ('nombre_completo', 'rol', 'telefono', 'estado_cuenta')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información Adicional', {'fields': ('nombre_completo', 'rol', 'telefono', 'estado_cuenta')}),
    )

admin.site.register(Paciente)
admin.site.register(Especialidad)
admin.site.register(Consultorio)
admin.site.register(Especialista)
admin.site.register(HorarioLaboral)
admin.site.register(Cita)
admin.site.register(AusenciasPermisos)

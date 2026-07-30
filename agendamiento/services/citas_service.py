"""
Capa de Servicios para la lógica del agendamiento y validación de Reglas de Negocio (RN01 - RN04).
"""

def validar_reprogramacion(cita, fecha_nueva):
    # RN01: Máximo 1 reprogramación desde autogestión web
    # RN02: Anticipación mayor a 24 horas
    pass

def registrar_inasistencia(paciente):
    # RN03 & RN04: Grace period de 20 min y bloqueo automático al acumular 3 inasistencias
    pass

"""
Servicio de Notificaciones Automáticas (HU10 / RF14)
Gestiona el envío de correos electrónicos y alertas del sistema al paciente y recepción.
"""
from django.core.mail import send_mail
from django.conf import settings

def notificar_confirmacion_cita(cita):
    """Notifica al paciente por correo cuando su cita es programada o creada."""
    asunto = f"Confirmación de Cita Médica - Pulsia (#{cita.id})"
    paciente_user = cita.paciente.usuario
    
    mensaje = (
        f"Hola {paciente_user.nombre_completo},\n\n"
        f"Tu cita médica ha sido confirmada exitosamente.\n\n"
        f"Detalles de la Cita:\n"
        f"- Especialista: Dr/Dra. {cita.especialista.usuario.nombre_completo}\n"
        f"- Especialidad: {cita.especialista.especialidad.nombre_especialidad}\n"
        f"- Consultorio: {cita.consultorio.nombre_codigo}\n"
        f"- Fecha y Hora: {cita.fecha_hora_inicio.strftime('%Y-%m-%d %H:%M')}\n\n"
        f"Gracias por confiar en Pulsia."
    )
    
    _enviar_correo_seguro(asunto, mensaje, paciente_user.correo)

def notificar_reprogramacion_cita(cita):
    """Notifica al paciente cuando su cita ha sido reprogramada."""
    asunto = f"Actualización de Cita Médica (Reprogramada) - Pulsia (#{cita.id})"
    paciente_user = cita.paciente.usuario
    
    mensaje = (
        f"Hola {paciente_user.nombre_completo},\n\n"
        f"Tu cita médica ha sido reprogramada.\n\n"
        f"Nuevos Detalles:\n"
        f"- Especialista: Dr/Dra. {cita.especialista.usuario.nombre_completo}\n"
        f"- Consultorio: {cita.consultorio.nombre_codigo}\n"
        f"- Fecha y Hora: {cita.fecha_hora_inicio.strftime('%Y-%m-%d %H:%M')}\n\n"
        f"Si no reconoces este cambio, contacta a recepción."
    )
    _enviar_correo_seguro(asunto, mensaje, paciente_user.correo)

def notificar_cancelacion_institucional(cita, motivo="Ausencia médica de emergencia"):
    """Dispara correo de disculpa institucional (RN08 / HU14) al paciente."""
    asunto = f"Aviso Importante: Cancelación Institucional de Cita - Pulsia (#{cita.id})"
    paciente_user = cita.paciente.usuario
    
    mensaje = (
        f"Estimado/a {paciente_user.nombre_completo},\n\n"
        f"Lamentamos informarle que su cita programada para {cita.fecha_hora_inicio.strftime('%Y-%m-%d %H:%M')} "
        f"con el/la Dr/Dra. {cita.especialista.usuario.nombre_completo} ha sido cancelada por imprevistos del centro médico ({motivo}).\n\n"
        f"Esta cancelación NO consume su oportunidad de reprogramación web. Su caso ha sido asignado con ALTA PRIORIDAD "
        f"a nuestra recepción para ser reubicado a la brevedad.\n\n"
        f"Ofrecemos nuestras sinceras disculpas."
    )
    _enviar_correo_seguro(asunto, mensaje, paciente_user.correo)

def notificar_lista_espera_liberacion(paciente, especialista, fecha_hora):
    """Notifica a un paciente en lista de espera que se liberó un cupo."""
    asunto = "¡Cupo disponible! - Lista de Espera Pulsia"
    paciente_user = paciente.usuario
    
    mensaje = (
        f"Hola {paciente_user.nombre_completo},\n\n"
        f"Se ha liberado un cupo con el/la Dr/Dra. {especialista.usuario.nombre_completo} "
        f"para la fecha {fecha_hora.strftime('%Y-%m-%d %H:%M')}.\n\n"
        f"Ingresa a tu portal web inmediatamente para confirmar la reserva."
    )
    _enviar_correo_seguro(asunto, mensaje, paciente_user.correo)

def _enviar_correo_seguro(asunto, mensaje, destinatario):
    """Intenta enviar el correo capturando cualquier error para no bloquear la transacción."""
    try:
        send_mail(
            asunto,
            mensaje,
            getattr(settings, 'DEFAULT_FROM_EMAIL', 'contacto@pulsia.com'),
            [destinatario],
            fail_silently=True
        )
    except Exception:
        pass

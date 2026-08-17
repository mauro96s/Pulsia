"""
Servicio de Notificaciones y Envío de Correos Electrónicos del Sistema Pulsia.
Soporta confirmaciones, cancelaciones, reprogramaciones y reubicaciones automáticas con diseño Pulsia y logo (HU10).
"""

import os
import logging
from email.mime.image import MIMEImage
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

logger = logging.getLogger(__name__)

def _adjuntar_logo_pulsia(email_obj):
    """Adjunta el logo institucional de Pulsia como imagen embebida cid:logo_pulsia."""
    try:
        logo_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'logo.png')
        if os.path.exists(logo_path):
            with open(logo_path, 'rb') as f:
                mime_img = MIMEImage(f.read())
                mime_img.add_header('Content-ID', '<logo_pulsia>')
                mime_img.add_header('Content-Disposition', 'inline', filename='logo.png')
                email_obj.attach(mime_img)
    except Exception as e:
        logger.warning(f"No se pudo adjuntar el logo al correo: {e}")


def _generar_plantilla_html(titulo_banner, subtitulo_banner, mensaje_principal, cita, nota_adicional=""):
    """Genera la plantilla HTML responsive con los colores y logo corporativo de Pulsia."""
    paciente_nombre = cita.paciente.usuario.nombre_completo
    medico_nombre = f"Dr/Dra. {cita.especialista.usuario.nombre_completo}"
    especialidad_nombre = cita.especialista.especialidad.nombre_especialidad
    consultorio_nombre = cita.consultorio.nombre_codigo if cita.consultorio else "Por Asignar"
    fecha_str = cita.fecha_hora_inicio.strftime('%d/%m/%Y')
    hora_inicio_str = cita.fecha_hora_inicio.strftime('%I:%M %p')
    hora_fin_str = cita.fecha_hora_fin.strftime('%I:%M %p')

    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{titulo_banner}</title>
    </head>
    <body style="margin: 0; padding: 0; background-color: #f1f5f9; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #1e293b;">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #f1f5f9; padding: 30px 10px;">
            <tr>
                <td align="center">
                    <table role="presentation" width="100%" style="max-width: 600px; background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.08); border: 1px solid #e2e8f0;">
                        <!-- HEADER CON LOGO Y COLORES PULSIA -->
                        <tr>
                            <td style="background-color: #003840; padding: 28px 24px; text-align: center;">
                                <table role="presentation" width="100%" cellspacing="0" cellpadding="0">
                                    <tr>
                                        <td align="center">
                                            <img src="cid:logo_pulsia" alt="Pulsia Centro Médico" style="max-height: 50px; width: auto; margin-bottom: 8px; display: block;" />
                                            <h1 style="color: #ffffff; margin: 0; font-size: 22px; font-weight: 700; letter-spacing: 0.5px;">Pulsia Centro Médico</h1>
                                            <p style="color: #80e5d9; margin: 4px 0 0 0; font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">{subtitulo_banner}</p>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>

                        <!-- CUERPO PRINCIPAL -->
                        <tr>
                            <td style="padding: 32px 28px;">
                                <h2 style="color: #003840; margin-top: 0; font-size: 18px; font-weight: 700;">Estimado(a) {paciente_nombre},</h2>
                                <p style="font-size: 14px; line-height: 1.6; color: #334155; margin-bottom: 24px;">{mensaje_principal}</p>

                                <!-- TARJETA RESUMEN DE LA CITA -->
                                <table role="presentation" width="100%" style="background-color: #f8fafc; border-left: 5px solid #00A896; border-radius: 12px; border: 1px solid #e2e8f0; border-left-width: 5px; margin-bottom: 24px; padding: 20px;">
                                    <tr>
                                        <td>
                                            <h3 style="color: #003840; margin: 0 0 16px 0; font-size: 15px; font-weight: 700; border-bottom: 1px solid #e2e8f0; padding-bottom: 8px;">
                                                Datos de la Cita Médica
                                            </h3>
                                            <table role="presentation" width="100%" cellspacing="0" cellpadding="6" style="font-size: 13px; color: #334155;">
                                                <tr>
                                                    <td width="35%" style="font-weight: 700; color: #475569;">Especialidad:</td>
                                                    <td style="font-weight: 600; color: #003840;">{especialidad_nombre}</td>
                                                </tr>
                                                <tr>
                                                    <td style="font-weight: 700; color: #475569;">Especialista:</td>
                                                    <td style="font-weight: 600; color: #003840;">{medico_nombre}</td>
                                                </tr>
                                                <tr>
                                                    <td style="font-weight: 700; color: #475569;">Consultorio:</td>
                                                    <td>
                                                        <span style="background-color: #003840; color: #ffffff; font-weight: 700; padding: 3px 8px; border-radius: 6px; font-size: 12px;">{consultorio_nombre}</span>
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <td style="font-weight: 700; color: #475569;">Fecha:</td>
                                                    <td style="font-weight: 700; color: #0f172a;">{fecha_str}</td>
                                                </tr>
                                                <tr>
                                                    <td style="font-weight: 700; color: #475569;">Horario:</td>
                                                    <td style="font-weight: 700; color: #00A896;">{hora_inicio_str} - {hora_fin_str}</td>
                                                </tr>
                                            </table>
                                        </td>
                                    </tr>
                                </table>

                                {f'<div style="background-color: #f0fdf4; border: 1px solid #bbf7d0; color: #166534; padding: 14px 16px; border-radius: 10px; font-size: 13px; margin-bottom: 20px;">{nota_adicional}</div>' if nota_adicional else ''}

                                <p style="font-size: 12px; color: #64748b; margin: 0; line-height: 1.5;">
                                    Recuerda presentarte <strong>15 minutos antes</strong> de la hora de tu cita. Si requieres modificar tu cita, puedes hacerlo directamente desde tu portal web con más de 24 horas de anticipación.
                                </p>
                            </td>
                        </tr>

                        <!-- FOOTER INSTITUCIONAL -->
                        <tr>
                            <td style="background-color: #f1f5f9; padding: 18px 24px; text-align: center; border-top: 1px solid #e2e8f0; font-size: 12px; color: #64748b;">
                                <p style="margin: 0 0 4px 0; font-weight: 600; color: #334155;">Pulsia Medical Systems — Centro de Gestión Clínica</p>
                                <p style="margin: 0;">Este es un mensaje automático de confirmación. Por favor no respondas a este correo.</p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """


def enviar_correo_confirmacion_cita(cita):
    """Envía correo de confirmación formal al crear una nueva cita médica."""
    try:
        paciente_user = cita.paciente.usuario
        correo_destino = paciente_user.correo
        if not correo_destino:
            return False

        fecha_str = cita.fecha_hora_inicio.strftime('%d/%m/%Y')
        hora_str = cita.fecha_hora_inicio.strftime('%I:%M %p')
        medico_str = f"Dr/Dra. {cita.especialista.usuario.nombre_completo}"
        especialidad_str = cita.especialista.especialidad.nombre_especialidad
        consultorio_str = cita.consultorio.nombre_codigo if cita.consultorio else "Por Asignar"

        asunto = f"[Pulsia] Confirmación de Cita Médica - {fecha_str}"
        mensaje_texto = (
            f"Estimado(a) {paciente_user.nombre_completo},\n\n"
            f"Tu cita médica ha sido agendada con éxito.\n\n"
            f"DETALLES DE LA CITA:\n"
            f"• Especialidad: {especialidad_str}\n"
            f"• Especialista: {medico_str}\n"
            f"• Consultorio: {consultorio_str}\n"
            f"• Fecha: {fecha_str}\n"
            f"• Hora: {hora_str}\n\n"
            f"Recuerda llegar 15 minutos antes.\n\n"
            f"Atentamente,\nPulsia Centro Médico"
        )

        mensaje_html = _generar_plantilla_html(
            titulo_banner="Confirmación de Cita Médica",
            subtitulo_banner="Reserva de Cita Confirmada",
            mensaje_principal="Nos complace informarte que tu cita médica ha sido agendada y registrada exitosamente en nuestro sistema.",
            cita=cita,
            nota_adicional="Tu cita se encuentra confirmada y reservada en la agenda del especialista."
        )

        remitente = getattr(settings, 'DEFAULT_FROM_EMAIL', 'brekapegi21082007@gmail.com')
        email = EmailMultiAlternatives(asunto, mensaje_texto, remitente, [correo_destino])
        email.attach_alternative(mensaje_html, "text/html")
        _adjuntar_logo_pulsia(email)
        email.send(fail_silently=False)
        logger.info(f"Correo de confirmación enviado a {correo_destino}.")
        return True
    except Exception as e:
        logger.error(f"Error al enviar correo de confirmación: {e}")
        return False


def enviar_correo_reprogramacion_cita(cita):
    """Envía correo de notificación al paciente cuando su cita es reprogramada."""
    try:
        paciente_user = cita.paciente.usuario
        correo_destino = paciente_user.correo
        if not correo_destino:
            return False

        fecha_str = cita.fecha_hora_inicio.strftime('%d/%m/%Y')
        hora_inicio_str = cita.fecha_hora_inicio.strftime('%I:%M %p')
        hora_fin_str = cita.fecha_hora_fin.strftime('%I:%M %p')
        medico_str = f"Dr/Dra. {cita.especialista.usuario.nombre_completo}"
        especialidad_str = cita.especialista.especialidad.nombre_especialidad
        consultorio_str = cita.consultorio.nombre_codigo if cita.consultorio else "Por Asignar"

        asunto = f"[Pulsia] Reprogramación de Cita Médica - {fecha_str}"
        mensaje_texto = (
            f"Estimado(a) {paciente_user.nombre_completo},\n\n"
            f"Tu cita médica ha sido reprogramada con éxito.\n\n"
            f"NUEVOS DETALLES:\n"
            f"• Especialidad: {especialidad_str}\n"
            f"• Especialista: {medico_str}\n"
            f"• Consultorio: {consultorio_str}\n"
            f"• Fecha: {fecha_str}\n"
            f"• Horario: {hora_inicio_str} a {hora_fin_str}\n\n"
            f"Recuerda llegar 15 minutos antes.\n\n"
            f"Atentamente,\nPulsia Centro Médico"
        )

        mensaje_html = _generar_plantilla_html(
            titulo_banner="Reprogramación de Cita Médica",
            subtitulo_banner="Cita Actualizada Exitosamente",
            mensaje_principal="Te notificamos que tu cita médica ha sido reprogramada. A continuación encontrarás los nuevos detalles actualizados de tu atención:",
            cita=cita,
            nota_adicional="Tu nueva cita ha sido reservada en la agenda del especialista."
        )

        remitente = getattr(settings, 'DEFAULT_FROM_EMAIL', 'brekapegi21082007@gmail.com')
        email = EmailMultiAlternatives(asunto, mensaje_texto, remitente, [correo_destino])
        email.attach_alternative(mensaje_html, "text/html")
        _adjuntar_logo_pulsia(email)
        email.send(fail_silently=False)
        logger.info(f"Correo de reprogramación enviado a {correo_destino}.")
        return True
    except Exception as e:
        logger.error(f"Error al enviar correo de reprogramación: {e}")
        return False


def enviar_correo_reubicacion_cita(cita, medico_anterior=None, motivo="reubicación por contingencia médica"):
    """Envía correo formal notificando la reubicación institucional de cita médica por falta o ausencia del especialista (HU10 / RN08)."""
    try:
        paciente_user = cita.paciente.usuario
        correo_destino = paciente_user.correo
        if not correo_destino:
            return False

        fecha_str = cita.fecha_hora_inicio.strftime('%d/%m/%Y')
        especialidad_nombre = cita.especialista.especialidad.nombre_especialidad
        medico_previo_str = f"Dr/Dra. {medico_anterior.usuario.nombre_completo}" if medico_anterior else "su médico asignado"

        asunto = f"[Pulsia] Reasignación Automática de Cita Médica - {fecha_str}"
        mensaje_texto = (
            f"Estimado(a) {paciente_user.nombre_completo},\n\n"
            f"Le informamos que debido a una eventualidad asistencial con {medico_previo_str}, quien no podrá atenderle en el horario previsto, "
            f"su cita médica de {especialidad_nombre} ha sido REASIGNADA AUTOMÁTICAMENTE para garantizar su atención oportuna.\n\n"
            f"Atentamente,\nPulsia Centro Médico"
        )

        mensaje_html = _generar_plantilla_html(
            titulo_banner="Reasignación Automática de Cita",
            subtitulo_banner="Reubicación Institucional de Atención",
            mensaje_principal=f"Le informamos que debido a una novedad asistencial con <strong>{medico_previo_str}</strong> (el especialista no podrá atenderle), su cita de <strong>{especialidad_nombre}</strong> ha sido <strong>reasignada automáticamente</strong> con un nuevo especialista para garantizar su atención médica oportuna.",
            cita=cita,
            nota_adicional="Nota: Esta reubicación es una medida institucional y NO consume la reprogramación permitida en su portal web (Regla RN08)."
        )

        remitente = getattr(settings, 'DEFAULT_FROM_EMAIL', 'brekapegi21082007@gmail.com')
        email = EmailMultiAlternatives(asunto, mensaje_texto, remitente, [correo_destino])
        email.attach_alternative(mensaje_html, "text/html")
        _adjuntar_logo_pulsia(email)
        email.send(fail_silently=False)
        logger.info(f"Correo de reubicación enviado a {correo_destino}.")
        return True
    except Exception as e:
        logger.error(f"Error al enviar correo de reubicación: {e}")
        return False


def enviar_correo_cancelacion_cita(cita):
    """Envía correo de notificación al paciente cuando su cita es cancelada."""
    try:
        paciente_user = cita.paciente.usuario
        correo_destino = paciente_user.correo
        if not correo_destino:
            return False

        fecha_str = cita.fecha_hora_inicio.strftime('%d/%m/%Y')
        hora_str = cita.fecha_hora_inicio.strftime('%I:%M %p')

        asunto = f"[Pulsia] Cancelación de Cita Médica - {fecha_str}"
        mensaje_texto = (
            f"Estimado(a) {paciente_user.nombre_completo},\n\n"
            f"Te confirmamos que tu cita programada para el {fecha_str} a las {hora_str} ha sido cancelada.\n\n"
            f"Si deseas agendar una nueva cita, puedes hacerlo desde tu portal web o comunicándote con recepción.\n\n"
            f"Pulsia Centro Médico"
        )

        mensaje_html = _generar_plantilla_html(
            titulo_banner="Cancelación de Cita Médica",
            subtitulo_banner="Notificación de Cancelación",
            mensaje_principal=f"Te confirmamos que tu cita médica agendada para el día <strong>{fecha_str}</strong> a las <strong>{hora_str}</strong> ha sido cancelada.",
            cita=cita,
            nota_adicional="Si deseas agendar una nueva cita médica, puedes ingresar nuevamente a tu portal web o comunicarte con recepción."
        )

        remitente = getattr(settings, 'DEFAULT_FROM_EMAIL', 'brekapegi21082007@gmail.com')
        email = EmailMultiAlternatives(asunto, mensaje_texto, remitente, [correo_destino])
        email.attach_alternative(mensaje_html, "text/html")
        _adjuntar_logo_pulsia(email)
        email.send(fail_silently=False)
        logger.info(f"Correo de cancelación enviado a {correo_destino}.")
        return True
    except Exception as e:
        logger.error(f"Error al enviar correo de cancelación: {e}")
        return False



# 📋 Especificación y Contexto del Proyecto: Sistema de Agendamiento Médico

Este documento centraliza los actores, requisitos, reglas de negocio e historias de usuario para el desarrollo del **Sistema de Gestión y Agendamiento de Citas de Consulta Externa**, desarrollado en Python y PostgreSQL.

---

## 1. 👥 Actores del Sistema (Roles)

* **Administrador:** Configura parámetros generales del centro médico, aprueba/rechaza solicitudes de ausencia de los especialistas, gestiona especialidades, consultorios y cuentas de usuario.
* **Recepcionista:** Opera la agenda global sin restricciones de tiempo. Atiende llamadas, agendamientos presenciales, maneja retrasos/inasistencias y reasigna citas ante contingencias.
* **Especialista:** Revisa su agenda, registra su asistencia diaria (*Check-in*), marca citas como atendidas, ingresa notas clínicas al historial y solicita bloqueos de tiempo en su calendario.
* **Paciente:** Consulta la disponibilidad médica, autogestiona sus reservas y reprogramaciones web, visualiza su historial e ingresa a listas de espera ante agendas llenas.

---

## 2. ⚖️ Reglas de Negocio (RN)

Las siguientes condiciones lógicas representan reglas estrictas de la organización que el backend en Python debe validar antes de cualquier transacción en PostgreSQL:

* **RN01 - Límite de Reprogramación Web:** Un paciente puede reprogramar una misma cita un máximo de una (1) vez desde su interfaz de autogestión.
* **RN02 - Anticipación de Cambios:** No se permiten cancelaciones ni reprogramaciones desde la web si faltan menos de 24 horas para la hora pactada de la cita.
* **RN03 - Tolerancia de Llegada (*Grace Period*):** El paciente tiene un margen de tolerancia de 15 a 20 minutos. Superado este tiempo sin anunciarse en recepción, la cita cambia al estado **No Asistió** y libera al especialista.
* **RN04 - Penalización por Inasistencia (*No-Show*):** La acumulación de tres (3) estados **No Asistió** en el historial del paciente bloquea automáticamente su permiso de agendamiento web, obligándolo a tramitar sus citas únicamente por teléfono o recepción.
* **RN05 - Conflicto por Ausencias Aprobadas:** Si la administración aprueba una ausencia a un médico que ya tenía citas programadas, el sistema debe alertar al recepcionista para priorizar la reubicación de los pacientes afectados.
* **RN06 - Privacidad del Historial Clínico:** Un especialista únicamente podrá visualizar las notas o el historial previo de los pacientes que tengan una cita agendada con él o que haya atendido en el pasado.
* **RN07 - Cierre de Sesión por Inactividad:** Por seguridad de la información, si una sesión laboral permanece inactiva por más de 15 minutos, debe cerrarse automáticamente.
* **RN08 - Cancelación Institucional:** Si una cita se cancela por ausencia de emergencia del médico o fallas del centro médico, se notificará al paciente. Esta cancelación **no consume** la reprogramación permitida en **RN01** y otorga prioridad de reubicación.

---

## 3. 🎯 Historias de Usuario (Backlog Completo: 14 HU)

### Módulo de Autenticación y Citas (Web y Recepción)

#### HU01 - Autenticación y Acceso (Login)
> *Como* usuario del sistema (Administrador, Recepcionista, Especialista o Paciente),  
> *quiero* iniciar sesión con mi correo electrónico y contraseña en una pantalla segura,  
> *para* acceder a las funcionalidades correspondientes a mi rol.
* **Requisito Asociado:** RF01
* **Criterios de Aceptación:**
  * [ ] El sistema valida el formato del correo.
  * [ ] Las contraseñas se cotejan mediante encriptación (*hash*).
  * [ ] Se muestra un mensaje de error si las credenciales son incorrectas.
  * [ ] Redirección automática al panel correspondiente según el tipo de rol (`rol_usuario`).

#### HU02 - Agendamiento Web Autónomo
> *Como* paciente registrado,  
> *quiero* ver un calendario interactivo con la disponibilidad de los médicos,  
> *para* agendar mi cita médica desde cualquier lugar sin llamar a la clínica.
* **Requisito Asociado:** RF07, RF08
* **Criterios de Aceptación:**
  * [ ] Permite filtrar por Especialidad y Especialista.
  * [ ] Los bloques de tiempo donde el médico o el consultorio estén ocupados aparecen deshabilitados.
  * [ ] El paciente debe confirmar la aceptación del tratamiento de datos personales (*Habeas Data*).
  * [ ] La reserva se almacena con estado `Programada`.

#### HU03 - Reprogramación de Citas Web
> *Como* paciente,  
> *quiero* poder modificar la fecha y hora de una cita que ya tengo agendada,  
> *para* ajustarla a mis necesidades en caso de un imprevisto personal.
* **Requisito Asociado:** RF09 | **Reglas:** RN01, RN02
* **Criterios de Aceptación:**
  * [ ] El botón "Reprogramar" se bloquea/oculta si faltan menos de 24 horas para la cita.
  * [ ] El backend valida que el contador de reprogramaciones de esa cita sea 0.
  * [ ] Al reprogramarse, el horario original queda liberado para otros usuarios en tiempo real.

#### HU04 - Gestión de Permisos e Imprevistos del Médico
> *Como* especialista,  
> *quiero* solicitar el bloqueo temporal de mi agenda desde el sistema,  
> *para* poder ausentarme por calamidades, vacaciones o descansos médicos.
* **Requisito Asociado:** RF11 | **Regla:** RN05
* **Criterios de Aceptación:**
  * [ ] El especialista selecciona fecha de inicio, fin y redacta una justificación.
  * [ ] La solicitud ingresa a la tabla `ausencias_permisos` con estado `Pendiente`.
  * [ ] Al ser aprobada por Administración, bloquea la disponibilidad en la agenda web.
  * [ ] Si la ausencia se cruza con citas programadas, lanza una notificación de alerta a la recepción.

#### HU05 - Historial y Anotaciones Clínicas
> *Como* especialista,  
> *quiero* poder agregar notas y recomendaciones al registro de una cita finalizada,  
> *para* dejar constancia de la atención y que el paciente pueda consultarla después.
* **Requisito Asociado:** RF13 | **Regla:** RN06
* **Criterios de Aceptación:**
  * [ ] Solo se pueden escribir notas clínicas cuando la cita está en estado `Atendida`.
  * [ ] El médico solo tiene acceso a historiales de pacientes asociados a sus turnos.
  * [ ] Las recomendaciones se visualizan en la sección de historial del panel del paciente.

---

### Módulo Operativo y de Recepción

#### HU06 - Agendamiento y Control Administrativo
> *Como* recepcionista,  
> *quiero* tener un calendario global sin restricciones de tiempo,  
> *para* agendar, modificar o cancelar citas de cualquier paciente en caso de llamadas o atención presencial.
* **Requisito Asociado:** RF06
* **Criterios de Aceptación:**
  * [ ] La recepción puede agendar, cancelar o modificar ignorando la regla de las 24 horas.
  * [ ] Visualización simultánea de agendas médicas en una sola vista.
  * [ ] Capacidad de cambiar el estado manualmente (ej. cambiar a `En_Sala` cuando llega el paciente).

#### HU07 - Gestión de Inasistencias y Retrasos
> *Como* recepcionista,  
> *quiero* que el sistema aplique las reglas de tolerancia de espera e inasistencias,  
> *para* liberar los consultorios y penalizar los abusos del servicio.
* **Requisito Asociado:** RF12 | **Reglas:** RN03, RN04
* **Criterios de Aceptación:**
  * [ ] Tras 20 minutos sin ingreso, permite marcar o autoconfigurar la cita como `No_Asistio`.
  * [ ] Si el paciente acumula 3 estados `No_Asistio`, su autogestión web se desactiva.
  * [ ] En la interfaz del paciente penalizado se muestra el aviso para gestionar citas por teléfono.

#### HU08 - Configuración de Descansos y Festivos (Vía API / Configuración)
> *Como* administrador,  
> *quiero* configurar las franjas de almuerzo y consumir una API externa de días festivos (Ley Emiliani),  
> *para* evitar agendamientos en días cerrados o en las horas de descanso del profesional.
* **Requisito Asociado:** RF04, RF05
* **Criterios de Aceptación:**
  * [ ] El backend se integra con una API (o servicio) para inhabilitar días feriados nacionales en el calendario.
  * [ ] La tabla `horarios_laborales` valida horas fijas de descanso intermedio (`hora_inicio_descanso` a `hora_fin_descanso`).
  * [ ] Ningún horario marcado en festivo o en hora de almuerzo será mostrable al paciente.

#### HU09 - Sistema de Lista de Espera
> *Como* paciente,  
> *quiero* inscribirme en una lista de espera si mi especialista no tiene cupos cercanos,  
> *para* tomar un turno rápidamente si alguien más cancela su cita.
* **Requisito Asociado:** RF10
* **Criterios de Aceptación:**
  * [ ] Disposición de un botón "Unirse a lista de espera" en vistas de agenda llena.
  * [ ] Cuando se cancela una cita, el sistema envía una notificación a los usuarios en espera.
  * [ ] El cupo liberado se asigna por estricto orden al primer paciente que confirme la reserva.

#### HU10 - Notificaciones Automáticas
> *Como* paciente,  
> *quiero* recibir alertas en mi correo electrónico ante cualquier cambio en mis reservas,  
> *para* tener confirmación inmediata sobre mis citas, modificaciones o cancelaciones.
* **Requisito Asociado:** RF14
* **Criterios de Aceptación:**
  * [ ] Envío exitoso de correo al crear una cita en la plataforma.
  * [ ] Envío de correo en cancelaciones institucionales o voluntarias.
  * [ ] El mensaje indica claramente: Fecha, Hora, Especialista y Consultorio.

---

### Módulo de BI, Asistencia y Contingencias

#### HU11 - Generación de Reportes Administrativos (BI)
> *Como* administrador,  
> *quiero* visualizar reportes estadísticos sobre demanda y porcentajes de inasistencia,  
> *para* medir el rendimiento del centro médico y tomar decisiones administrativas.
* **Requisito Asociado:** REP01, REP02, REP03
* **Criterios de Aceptación:**
  * [ ] Gráfica/tabla con citas atendidas, canceladas e inasistencias por médico.
  * [ ] Reporte comparativo de especialidades más demandadas en el mes.
  * [ ] Métrica global de tasa de inasistencias (`No_Asistio` vs. Total de citas programadas).

#### HU12 - Gestión de Empleados y Catálogo de Especialidades (CRUD)
> *Como* administrador,  
> *quiero* gestionar las especialidades médicas, los consultorios y los usuarios del personal médico,  
> *para* mantener actualizada la estructura operativa del centro de consulta externa.
* **Requisito Asociado:** RF03, RF04
* **Criterios de Aceptación:**
  * [ ] Creación, lectura, edición y desactivación de registros en `especialidades` y `consultorios`.
  * [ ] Al crear un médico en `especialistas`, se le asigna su usuario, especialidad y horario de trabajo base.
  * [ ] El sistema impide eliminar un consultorio o especialidad si cuenta con citas futuras activas.

#### HU13 - Check-in Médico (Inicio de Turno)
> *Como* especialista,  
> *quiero* registrar mi llegada al centro médico desde mi interfaz al iniciar jornada,  
> *para* que recepción y el sistema verifiquen mi disponibilidad antes de llamar pacientes.
* **Requisito Asociado:** RF16 (Asistencia del especialista)
* **Criterios de Aceptación:**
  * [ ] Botón de acción "Iniciar Turno" en la vista principal del médico.
  * [ ] Al pulsarse, actualiza `estado_turno` a `Presente` en la base de datos.
  * [ ] Recepción visualiza el indicador en verde (`Presente`) o rojo (`Ausente`) en el calendario.

#### HU14 - Contingencia por Ausencia Médica de Emergencia
> *Como* recepcionista (o administrador),  
> *quiero* marcar a un especialista en "Ausencia de Emergencia" el día actual,  
> *para* bloquear el resto de su agenda y reubicar rápidamente a los pacientes que lo esperaban.
* **Requisito Asociado:** RF17 | **Regla:** RN08
* **Criterios de Aceptación:**
  * [ ] La acción cambia automáticamente el estado del especialista a `Ausente`.
  * [ ] Todas las citas futuras de ese profesional en el día cambian a `Pendiente_Reubicacion`.
  * [ ] Se dispara el correo de disculpa institucional (`RN08`) sin consumir la reprogramación al paciente.
  * [ ] La interfaz de recepción genera una lista priorizada de pacientes por reubicar.

---

## 4. 🗄️ Stack Tecnológico Definitivo (RNF)

* **Backend / Framework Web:** Python con **Django**. Se aprovechará la arquitectura MVT (Modelo-Vista-Plantilla), el ORM nativo para la gestión transaccional de datos y su módulo de seguridad integrado para autenticación y manejo de sesiones.
* **Base de Datos:** PostgreSQL (Relacional, con integridad referencial estricta, aprovechando migraciones nativas de Django y compatibilidad con tipos `TIMESTAMP`, `BOOLEAN` y `ENUM`).
* **Frontend (UI/UX):** Plantillas de Django (`Django Templates`) integradas con HTML5, JavaScript y maquetado moderno responsivo mediante **Tailwind CSS** (o Bootstrap).
* **Integraciones y APIs:** Consumo de API REST externa para la detección automática del calendario de festivos colombianos (Ley Emiliani) para el bloqueo dinámico de agendas.
* **Seguridad:** Encriptación de contraseñas nativa de Django (PBKDF2 por defecto), protección contra ataques CSRF/XSS en formularios y control de acceso por roles y permisos.
# Manual de Usuario - Pulsia Medical Systems

Este documento constituye la guía oficial de usuario para el **Sistema de Gestión y Agendamiento de Citas de Consulta Externa (Pulsia Medical Systems)**. Define el funcionamiento operativo, los flujos por cada rol de usuario, las reglas de negocio del sistema y las especificaciones exactas para la inclusión de capturas de pantalla de la interfaz.

---

## 1. Introducción y Ficha Técnica

### 1.1 Descripción General
Pulsia Medical Systems es una solución web integral diseñada para la optimización del proceso de agendamiento de citas médicas, control presencial en recepción, seguimiento del historial clínico por especialista y análisis de datos administrativos (BI).

### 1.2 Requisitos del Sistema y Navegadores Compatibles
Pulsia es una plataforma web accesible desde cualquier navegador moderno sin necesidad de instalar software adicional en su equipo o dispositivo.

- **Navegadores Web Compatibles:**
  - Google Chrome (versión 90 o superior recomendada).
  - Microsoft Edge (versión 90 o superior).
  - Mozilla Firefox (versión 88 o superior).
  - Apple Safari (versión 14 o superior).
- **Dispositivos Compatibles:** Computadores de escritorio, computadores portátiles, tabletas y teléfonos inteligentes con conexión a Internet.
- **Requisitos de Red:** Conexión a Internet activa y estable.

### 1.3 Diseño e Interfaz Adaptativa (UX)
La plataforma cuenta con un diseño intuitivo y responsivo que adapta automáticamente la disposición de los menús, tablas y botones según el tamaño del dispositivo (pantalla táctil de celular, tableta o monitor de computador).

#### Código Visual de Colores y Estados
El sistema utiliza una convención visual de colores en botones, tarjetas de estado y alertas para facilitar su uso:

- **Verde (Éxito y Confirmación):** Indica estados positivos, asistencias confirmadas o acciones completadas con éxito (ej. estado `✓ Asistió`, cita `Atendida`, médico en estado `Presente`).
- **Rojo / Rosa (Alertas, Inasistencias y Cancelaciones):** Señala faltas a citas, cancelaciones, registros de inasistencia o avisos de advertencia (ej. estado `✗ No Asistió`, médico `Ausente`, alerta por acumulación de 3 inasistencias).
- **Azul / Índigo (Acciones Principales e Información):** Identifica la navegación principal, botones primarios de acción y botones de confirmación (ej. `Agendar Cita`, `Iniciar Turno`, `Guardar Nota`).
- **Amarillo / Naranja (Estados Pendientes y Advertencias):** Indica procesos en revisión, solicitudes pendientes o citas en proceso de reasignación (ej. cita en estado `Pendiente Reubicación`, permiso `Pendiente`).
- **Gris (Deshabilitado / Inactivo):** Muestra opciones o días no disponibles según las reglas del sistema (ej. días pasados deshabilitados en el calendario, botones de reprogramación inactivos por faltar menos de 24 horas).

### 1.4 Roles de Usuario y Matriz de Acceso

| Rol | Alcance y Funcionalidad | Permisos Principales |
| :--- | :--- | :--- |
| **Paciente** | Autogestión de citas web y consulta de historial. | Agendar citas, reprogramar (1 vez), cancelar, unirse a lista de espera, ver recomendaciones. |
| **Especialista** | Control de agenda médica y atención clínica. | Registrar asistencia (Check-in), marcar citas como atendidas, escribir notas clínicas, solicitar permisos. |
| **Recepcionista** | Operación presencial, telefónica y de contingencia. | Agenda global multimédico, marcación de asistencia (En Sala / No Asistió), reubicación de citas. |
| **Administrador** | Configuración institucional y análisis BI. | Gestión de usuarios, especialidades, consultorios, aprobación de ausencias y reportes estadísticos. |

---

## 2. Acceso y Autenticación al Sistema

### 2.1 Inicio de Sesión (`/login/`)
1. Ingrese a la dirección web del sistema en su navegador.
2. Introduzca su correo electrónico registrado y contraseña.
3. El sistema validará sus credenciales de manera segura. Al autenticarse correctamente, el servidor redirigirá automáticamente al tablero (*Dashboard*) correspondiente a su rol.

> [!NOTE]
> **CAPTURA RECOMENDADA #01: Formulario de Inicio de Sesión**
> - **Ruta en el sistema:** `/login/`
> - **Zona a capturar:** Tarjeta central del formulario de login, incluyendo los campos de correo, contraseña, botón "Iniciar Sesión" y el enlace de registro.
> - **Propósito:** Mostrar la interfaz de ingreso de credenciales para todos los roles.
> - **Ubicación de archivo sugerida:** `doc/img/captura_01_login.png`

---

### 2.2 Registro Autónomo de Pacientes (`/register/`)
Los usuarios nuevos que deseen solicitar citas como pacientes pueden registrarse de manera autónoma:
1. Haga clic en **"Registrarse aquí"** en la pantalla de inicio de sesión.
2. Complete el formulario con sus datos personales: Tipo y número de documento, nombre completo, correo electrónico, teléfono y contraseña.
3. El sistema asignará automáticamente el rol **Paciente**.

> [!NOTE]
> **CAPTURA RECOMENDADA #02: Formulario de Registro de Paciente**
> - **Ruta en el sistema:** `/register/`
> - **Zona a capturar:** Formulario completo de registro con sus campos de datos personales y botón "Crear Cuenta".
> - **Propósito:** Ilustrar el procedimiento de auto-registro exclusivo para pacientes.
> - **Ubicación de archivo sugerida:** `doc/img/captura_02_registro_paciente.png`

---

### 2.3 Política de Cierre de Sesión por Inactividad (Regla RN07)
Por motivos de seguridad y confidencialidad de la información médica:
- Las sesiones de los usuarios con roles internos (**Administrador**, **Recepcionista** y **Especialista**) expirarán automáticamente tras **15 minutos** de inactividad continua.
- Al expirar la sesión, el sistema redirigirá al usuario a la pantalla de login requiriendo una nueva autenticación.

---

## 3. Manual del Usuario: Rol Paciente

### 3.1 Tablero Principal del Paciente (`/dashboard/paciente/`)
Al ingresar, el paciente dispone de una interfaz organizada en pestañas principales:
- **Inicio:** Resumen de accesos rápidos y tarjeta de la próxima cita médica programada.
- **Mis Citas:** Listado completo de citas activas e históricas.
- **Historial y Recomendaciones:** Registro de atenciones finalizadas con las notas médicas dejadas por los especialistas.

> [!NOTE]
> **CAPTURA RECOMENDADA #03: Dashboard Principal del Paciente**
> - **Ruta en el sistema:** `/dashboard/paciente/`
> - **Zona a capturar:** Vista superior del portal paciente, mostrando la barra de navegación horizontal (Inicio, Mis Citas, Historial) y la tarjeta resumen de la próxima cita.
> - **Propósito:** Presentar el panel de control inicial del paciente.
> - **Ubicación de archivo sugerida:** `doc/img/captura_03_dashboard_paciente.png`

---

### 3.2 Agendamiento Web Autónomo (`/citas/agendar/`)
Para agendar una nueva cita médica de forma autónoma:

1. **Selección de Filtros:** Elija la **Especialidad** médica requerida y el **Médico Especialista**.
2. **Selección de Fecha:** Utilice el calendario mensual interactivo situado en la parte izquierda. Los días pasados o festivos (Ley Emiliani) se mostrarán deshabilitados.
3. **Selección de Franja Horaria:** Seleccione la hora deseada de la grilla de bloques de 30 minutos disponibles en el panel derecho.
4. **Confirmación y Habeas Data:** En el modal desplegado, revise el médico, fecha, hora y consultorio asignado automáticamente. Marque de manera obligatoria la casilla de aceptación de **Tratamiento de Datos Personales (Habeas Data)** y presione **"Confirmar Cita"**.

> [!NOTE]
> **CAPTURA RECOMENDADA #04: Interfaz de Agendamiento Web (Vista Split 50/50)**
> - **Ruta en el sistema:** `/citas/agendar/`
> - **Zona a capturar:** Interfaz principal de reserva mostrando a la izquierda el calendario mensual interactivo y a la derecha los desplegables de especialidad/médico con la grilla de horas disponibles.
> - **Propósito:** Guiar al paciente en el proceso de selección de fecha y franja horaria.
> - **Ubicación de archivo sugerida:** `doc/img/captura_04_agendamiento_split.png`

> [!NOTE]
> **CAPTURA RECOMENDADA #05: Modal de Confirmación y Consentimiento de Habeas Data**
> - **Ruta en el sistema:** Ventana emergente sobre `/citas/agendar/`
> - **Zona a capturar:** Modal de resumen de reserva con los detalles de la cita, la casilla de verificación de Habeas Data y el botón de confirmación final.
> - **Propósito:** Mostrar la validación previa y aceptación de política de datos antes de guardar la cita.
> - **Ubicación de archivo sugerida:** `doc/img/captura_05_modal_habeas_data.png`

---

### 3.3 Reprogramación y Cancelación de Citas

#### Reglas Estrictas de Reprogramación Web:
- **Límite de Reprogramación (RN01):** Una misma cita solo puede reprogramarse **una (1) sola vez** a través del portal web.
- **Anticipación Mínima de 24 Horas (RN02):** No es posible reprogramar ni cancelar citas si faltan menos de 24 horas para la fecha y hora pactada.

#### Pasos para Reprogramar:
1. Ingrese a la sección **"Mis Citas"**.
2. Ubique la cita deseada y haga clic en el botón **"Reprogramar"**.
3. Seleccione la nueva fecha u hora requerida y confirme la actualización.

> [!NOTE]
> **CAPTURA RECOMENDADA #06: Sección "Mis Citas" y Botón de Reprogramación**
> - **Ruta en el sistema:** `/dashboard/paciente/` (Pestaña "Mis Citas")
> - **Zona a capturar:** Listado de citas del paciente detallando el estado de cada una y la presencia/ausencia del botón "Reprogramar" según las reglas RN01 y RN02.
> - **Propósito:** Explicar cómo el paciente gestiona o modifica sus reservas activas.
> - **Ubicación de archivo sugerida:** `doc/img/captura_06_mis_citas_reprogramar.png`

---

### 3.4 Penalización por Inasistencia / No-Show (Regla RN04)
Si un paciente falta a sus citas agendadas sin cancelar previamente:
- Cada inasistencia se registra en su historial acumulando el estado `No Asistió`.
- Al sumar **tres (3) inasistencias acumuladas**, el sistema deshabilita automáticamente la opción de agendamiento autónomo por la web.
- Aparecerá un aviso en su pantalla notificándole que sus próximas citas deberán ser tramitadas exclusivamente por atención telefónica o en recepción.

> [!NOTE]
> **CAPTURA RECOMENDADA #07: Alerta de Penalización por Inasistencias (No-Show)**
> - **Ruta en el sistema:** `/citas/agendar/` o Tablero Paciente
> - **Zona a capturar:** Cuadro de diálogo o banner de advertencia notificando al paciente el bloqueo del agendamiento web tras acumular 3 inasistencias.
> - **Propósito:** Mostrar la consecuencia visual del cumplimiento de la regla RN04.
> - **Ubicación de archivo sugerida:** `doc/img/captura_07_alerta_penalizacion.png`

---

### 3.5 Inscripción en Lista de Espera (HU09)
Cuando la agenda de un médico especialista o especialidad se encuentre totalmente llena en la fecha deseada:
1. El sistema habilitará la opción **"Unirse a Lista de Espera"**.
2. Al registrarse, si otro paciente cancela su cita, el sistema enviará una notificación por correo electrónico a los integrantes de la lista para tomar el cupo liberado por orden de respuesta.

---

## 4. Manual del Usuario: Rol Especialista Médico

### 4.1 Registro de Asistencia / Check-in de Turno (HU13)
Al iniciar su jornada laboral en el centro médico:
1. El médico ingresa a su panel (`/dashboard/especialista/`).
2. Debe hacer clic en el botón superior **"Iniciar Turno (Check-in)"**.
3. Al ejecutar la acción, su estado cambiará a `Presente`. Esto permite a recepción saber que el médico está listo para recibir pacientes en su consultorio.

> [!NOTE]
> **CAPTURA RECOMENDADA #08: Dashboard Especialista y Botón de Check-in**
> - **Ruta en el sistema:** `/dashboard/especialista/`
> - **Zona a capturar:** Cabecera del tablero médico mostrando el indicador de estado del turno (Ausente/Presente) y el botón de acción "Iniciar Turno".
> - **Propósito:** Explicar el procedimiento diario de marcación de asistencia del especialista.
> - **Ubicación de archivo sugerida:** `doc/img/captura_08_checkin_medico.png`

---

### 4.2 Atención de Pacientes y Registro de Notas Clínicas (HU05 y RN06)
1. En la agenda del día, el especialista visualiza los pacientes en estado `En Sala` (anunciados por recepción).
2. Tras realizar la consulta, el médico selecciona la cita y cambia su estado a **"Atendida"**.
3. Se desplegará el modal de **Notas Clínicas e Historial**, donde podrá redactar el diagnóstico, prescripciones o recomendaciones.

> [!IMPORTANT]
> **Privacidad del Historial Clínico (RN06):** Por normativa de protección de datos médicos, el especialista solo podrá consultar el historial y escribir notas de pacientes que tengan o hayan tenido una cita agendada de forma directa con él.

> [!NOTE]
> **CAPTURA RECOMENDADA #09: Agenda Diaria del Especialista y Modal de Notas Clínicas**
> - **Ruta en el sistema:** `/dashboard/especialista/`
> - **Zona a capturar:** Tabla de pacientes asignados del día y la ventana emergente para el ingreso del resumen clínico y recomendaciones.
> - **Propósito:** Ilustrar el flujo de cierre de cita médica e ingreso de observaciones profesionales.
> - **Ubicación de archivo sugerida:** `doc/img/captura_09_notas_clinicas_modal.png`

---

### 4.3 Solicitud de Permisos y Ausencias Medicas (HU04 y RN05)
Cuando un especialista requiera ausentarse por vacaciones, congresos o calamidad:
1. Acceda al módulo de **"Solicitar Permiso"**.
2. Complete la fecha de inicio, fecha de fin y la justificación correspondiente.
3. La solicitud ingresará con estado `Pendiente` a la bandeja de la administración.
4. Al ser aprobada por el Administrador, el sistema bloqueará automáticamente la disponibilidad en el calendario web. Si existían citas agendadas en ese rango, se generará una alerta de reubicación a Recepción (RN05).

> [!NOTE]
> **CAPTURA RECOMENDADA #10: Formulario de Solicitud de Permiso del Médico**
> - **Ruta en el sistema:** `/especialistas/permiso/` o pestaña de ausencias
> - **Zona a capturar:** Formulario con los selectores de rango de fechas, campo de texto para la justificación y botón de envío de la solicitud.
> - **Propósito:** Mostrar el trámite de suspensión temporal de agenda médica.
> - **Ubicación de archivo sugerida:** `doc/img/captura_10_solicitud_permiso.png`

---

## 5. Manual del Usuario: Rol Recepcionista

### 5.1 Agenda Global Multimédico (`/dashboard/recepcion/`)
La recepción opera una vista unificada que permite gestionar la atención presencial y telefónica:
- **Barra de Filtros:** Filtrado simultáneo por Especialidad, Nombre del Especialista o Cédula/Nombre del Paciente.
- **Acceso Exento de Restricciones:** A diferencia del paciente web, la recepción puede agendar o modificar citas sin la limitante de las 24 horas previas.

> [!NOTE]
> **CAPTURA RECOMENDADA #11: Vista General del Tablero de Recepción**
> - **Ruta en el sistema:** `/dashboard/recepcion/`
> - **Zona a capturar:** Pantalla principal de recepción con los filtros superiores de búsqueda y la grilla o tabla multimédico de la jornada.
> - **Propósito:** Presentar el centro de control de atención presencial de recepción.
> - **Ubicación de archivo sugerida:** `doc/img/captura_11_dashboard_recepcion.png`

---

### 5.2 Control de Llegadas y Tolerancia de Espera (HU07 y RN03)

#### Acciones Directas en Recepción:
- **Marcar `✓ Asistió`:** Cuando el paciente se presenta en recepción, el operador pulsa este botón. La cita cambia inmediatamente al estado `En Sala`, notificando al médico.
- **Marcar `✗ No Asistió`:** Si el paciente confirma que no asistirá o supera la tolerancia.

#### Tolerancia de Espera (Margen Grace Period - RN03):
- El sistema cuenta con un margen de tolerancia predeterminado de **15 a 20 minutos**.
- Si un paciente no ha sido marcado como presente tras superar este margen desde la hora pactada, el sistema convertirá automáticamente la cita a estado `No Asistió`, liberando al especialista para el siguiente turno.

> [!NOTE]
> **CAPTURA RECOMENDADA #12: Botones de Acción Rápida de Llegada en Recepción**
> - **Ruta en el sistema:** `/dashboard/recepcion/`
> - **Zona a capturar:** Fila de la tabla de citas destacando los botones de acción presencial "Asistió (En Sala)" y "No Asistió".
> - **Propósito:** Ilustrar la gestión de flujo de pacientes a su llegada a la clínica.
> - **Ubicación de archivo sugerida:** `doc/img/captura_12_acciones_llegada_recepcion.png`

---

### 5.3 Atención de Contingencias y Reubicación Prioritaria de Citas
Cuando la Administración declara la ausencia de emergencia de un médico o se aprueba una ausencia que interfiere con citas del día:

1. **Notificación en Recepción:** En el tablero principal de recepción (`/dashboard/recepcion/`) se activa automáticamente el banner destacado **"Citas Prioritarias Pendientes de Reubicación"**.
2. **Revisión de Pacientes Afectados:** La recepcionista visualiza la lista de pacientes cuyas citas fueron suspendidas por la contingencia médica.
3. **Reubicación de Citas:** La recepción procede a reasignar al paciente con otro médico disponible de la misma especialidad o en un nuevo horario conveniente.

> [!IMPORTANT]
> **Protección del Paciente:** La cancelación o suspensión institucional por imprevisto del centro médico **no consume** la oportunidad de reprogramación web del paciente y le otorga máxima prioridad en la cola de atención de recepción.

> [!NOTE]
> **CAPTURA RECOMENDADA #13: Banner de Citas Prioritarias Pendientes de Reubicación**
> - **Ruta en el sistema:** `/dashboard/recepcion/`
> - **Zona a capturar:** Banner destacado de "Citas Prioritarias Pendientes de Reubicación" en la parte superior del tablero de recepción con el listado de pacientes afectados.
> - **Propósito:** Mostrar cómo la recepción identifica y atiende a los pacientes cuya cita requiere reubicación prioritaria.
> - **Ubicación de archivo sugerida:** `doc/img/captura_13_reubicacion_contingencia.png`

---

## 6. Manual del Usuario: Rol Administrador

### 6.1 Tablero Principal de Administración (`/dashboard/admin/`)
El Administrador dispone de un panel centralizado para la gestión operativa, configuración de parámetros y análisis estratégico del centro médico.

> [!NOTE]
> **CAPTURA RECOMENDADA #14: Dashboard del Administrador**
> - **Ruta en el sistema:** `/dashboard/admin/`
> - **Zona a capturar:** Vista principal del administrador con los accesos directos a Usuarios, Estructura Médica, Permisos y Reportes BI.
> - **Propósito:** Mostrar el menú de control global del sistema.
> - **Ubicación de archivo sugerida:** `doc/img/captura_14_dashboard_admin.png`

---

### 6.2 Gestión de Usuarios y Personal (HU12)
- Acceso a `/admin/usuarios/`.
- Permite la creación, edición, cambio de estado (Activo/Inactivo) y asignación de roles para Administradores, Recepcionistas, Especialistas y Pacientes.

> [!NOTE]
> **CAPTURA RECOMENDADA #15: Modulo de Gestion de Usuarios**
> - **Ruta en el sistema:** `/administracion/usuarios/` (o vista admin correspondiente)
> - **Zona a capturar:** Tabla de administración de cuentas de usuario con filtros por rol, estado y opciones de edición.
> - **Propósito:** Explicar cómo se crean y administran los accesos del personal.
> - **Ubicación de archivo sugerida:** `doc/img/captura_15_gestion_usuarios.png`

---

### 6.3 Gestión de Estructura Médica (Especialidades y Consultorios)
- Acceso a `/admin/estructura-medica/`.
- Permite crear y actualizar el catálogo de especialidades clínicas y la asignación fija de consultorios físicos a los médicos.

> [!NOTE]
> **CAPTURA RECOMENDADA #16: Configuración de Especialidades y Consultorios**
> - **Ruta en el sistema:** `/administracion/estructura-medica/`
> - **Zona a capturar:** Formularios de alta/edición de especialidades y asignación de consultorios a médicos especialistas.
> - **Propósito:** Mostrar la parametrización de la infraestructura física y médica.
> - **Ubicación de archivo sugerida:** `doc/img/captura_16_estructura_medica.png`

---

### 6.4 Aprobación de Permisos y Declaración de Ausencias de Emergencia
- **Bandeja de Permisos (`/administracion/permisos/`):** El Administrador revisa las solicitudes enviadas por los especialistas y selecciona **Aprobar** o **Rechazar**.
- **Declarar Ausencia de Emergencia:** En la parte superior del módulo de permisos, el Administrador dispone del botón **"Declarar Ausencia de Emergencia"** para bloquear la agenda de un médico de forma inmediata en el día de hoy ante cualquier imprevisto.
- Al aprobar o declarar la ausencia, el sistema convierte las citas afectadas al estado `Pendiente Reubicación` y envía las notificaciones a los pacientes y a Recepción.

> [!NOTE]
> **CAPTURA RECOMENDADA #17: Bandeja de Permisos y Declaración de Ausencia de Emergencia**
> - **Ruta en el sistema:** `/administracion/permisos/`
> - **Zona a capturar:** Pantalla de gestión de permisos del Administrador, incluyendo el botón "Declarar Ausencia de Emergencia" y la lista de solicitudes.
> - **Propósito:** Ilustrar el flujo administrativo de aprobación de permisos y activación de contingencias médicas.
> - **Ubicación de archivo sugerida:** `doc/img/captura_17_bandeja_permisos.png`

---

### 6.5 Tablero de Inteligencia de Negocios BI y Reportes (HU11)
Acceso al módulo de métricas analíticas (`/reportes/bi/`):
- **Tasa Global de Inasistencia:** Muestra la relación porcentual entre citas programadas vs. estado `No Asistió`.
- **Especialidades de Mayor Demanda:** Gráfico comparativo del volumen de reservas por especialidad.
- **Rendimiento por Médico:** Métricas de citas atendidas, canceladas e inasistencias por especialista.

> [!NOTE]
> **CAPTURA RECOMENDADA #18: Tablero de Reportes BI y Graficos Estadisticos**
> - **Ruta en el sistema:** `/reportes/bi/`
> - **Zona a capturar:** Pantalla completa de reportes mostrando las tarjetas de indicadores de desempeño (KPIs) y los gráficos estadísticos.
> - **Propósito:** Presentar el módulo de analítica estratégica para la toma de decisiones administrativas.
> - **Ubicación de archivo sugerida:** `doc/img/captura_18_reportes_bi.png`

---

## 7. Anexo: Credenciales de Prueba

Para pruebas de evaluación o demostración en entorno de pruebas, utilice las siguientes cuentas (Contraseña universal: `123456`):

| Rol | Correo Electrónico | Contraseña | Dashboard de Destino |
| :--- | :--- | :--- | :--- |
| **Administrador** | `andi@pulsia.com` | `123456` | `/dashboard/admin/` |
| **Recepcionista** | `roca@pulsia.com` | `123456` | `/dashboard/recepcion/` |
| **Especialista (Medicina General)** | `cape@pulsia.com` | `123456` | `/dashboard/especialista/` |
| **Especialista (Cardiología)** | `anso@pulsia.com` | `123456` | `/dashboard/especialista/` |
| **Paciente** | `pema@pulsia.com` | `123456` | `/dashboard/paciente/` |

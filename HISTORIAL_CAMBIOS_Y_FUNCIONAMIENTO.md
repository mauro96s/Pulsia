# 📖 Documentación de Funcionamiento y Historial de Cambios — Pulsia

Este documento resume la arquitectura actual de **Pulsia**, las reglas de negocio implementadas, los campos adicionales creados en PostgreSQL/Django, y las mejoras de interfaz desarrolladas para que todo el equipo conozca el funcionamiento detallado del software.

---

## 🗄️ 1. Modificaciones y Nuevos Campos en la Base de Datos

Para dar cumplimiento a los requerimientos operacionales y reglas estrictas de negocio, se agregaron los siguientes campos a los modelos existentes:

### 🔹 Modelo `Cita` (`agendamiento/models/citas.py`)
- **`contador_reprogramacion` (IntegerField, default=0):**
  - **Propósito:** Almacena la cantidad de veces que una cita ha sido reprogramada por el paciente vía web.
  - **Uso:** Implementa la regla **RN01**, impidiendo que una cita sea reprogramada más de 1 vez desde la web.

### 🔹 Modelo `Especialista` (`agendamiento/models/especialistas.py`)
- **`consultorio_asignado` (ForeignKey -> Consultorio, null=True, blank=True):**
  - **Propósito:** Vincula de forma fija a un especialista con su consultorio asignado en la clínica.
  - **Uso:** Permite mostrar automáticamente el número de consultorio al paciente desde el momento en que elige su médico en el agendamiento web.
- **`estado_turno` (Choices: `'Presente'`, `'Ausente'`):**
  - **Propósito:** Muestra el estado del *Check-in* diario del médico para información de recepción.

### 🔹 Modelo `Paciente` (`agendamiento/models/pacientes.py`)
- **`contador_inasistencias` (IntegerField, default=0):**
  - **Propósito:** Lleva el registro acumulado de veces que el paciente ha faltado a una cita (`NO_ASISTIO`).
  - **Uso:** Implementa la regla **RN04**. Al llegar a **3 inasistencias**, el sistema bloquea automáticamente la autogestión web del paciente.
- **`acepta_habeas_data` (BooleanField, default=False):**
  - **Propósito:** Registro obligatorio de aceptación de tratamiento de datos personales en salud.

---

## ⚖️ 2. Implementación de las 8 Reglas de Negocio Estrictas (RN)

| Código | Regla de Negocio | Implementación Técnica en el Sistema |
| :--- | :--- | :--- |
| **RN01** | **Límite Reprogramación Web** | Max 1 reprogramación por cita. Validado en `citas_service.py` con `contador_reprogramacion`. |
| **RN02** | **Anticipación 24 Horas** | Bloquea cancelaciones/reprogramaciones web si faltan menos de 24 horas para la cita. |
| **RN03** | **Tolerancia 15 Minutos** | Evaluado en tiempo real al abrir el panel de Recepción y en el comando `marcar_inasistencias.py`. Citas con >15 min de retraso cambian a `NO_ASISTIO`. |
| **RN04** | **Penalización (No-Show)** | Al sumar 3 `NO_ASISTIO`, la interfaz web deshabilita el botón de agendar y muestra alerta al paciente. |
| **RN05** | **Conflicto por Ausencias** | Al aprobar una ausencia médica en `admin_views.py`, las citas cruzadas cambian a `PENDIENTE_REUBICACION` de forma prioritaria. |
| **RN06** | **Privacidad del Historial** | `dashboard_views.py` filtra las notas clínicas para que los especialistas solo accedan a historiales de sus pacientes. |
| **RN07** | **Inactividad (15 Minutos)** | En `auth_views.py`, los roles internos (Admin, Recepcionista, Especialista) tienen `set_expiry(900)` para cerrar sesión tras 15 min sin uso. |
| **RN08** | **Cancelación Institucional** | Cancelaciones por contingencia no consumen la cuota de reprogramación del paciente y envían correo de disculpas institucionales (`citas_service.py`). |

---

## 🖥️ 3. Flujos de Interfaz y Vistas Principales

### 🅰️ Módulo del Paciente (`agendar.html` y `paciente_dashboard.html`)
1. **Accesos Rápidos "Médicos Preferidos":** Muestra tarjetas con los especialistas previamente consultados para agendar en 1 clic.
2. **Layout 50/50 Split:**
   - **Lado Izquierdo (50%):** Calendario mensual interactivo con navegación entre meses, resaltado del día de hoy y días pasados deshabilitados.
   - **Lado Derecho (50%):** Seleccionadores de Especialidad y Médico con ficha resumen en tiempo real.
3. **Sección Inferior de Horarios:** Grilla dinámica con franjas de 30 minutos disponibles según la fecha elegida.
4. **Modal de Confirmación:** Resumen con médico, fecha, hora, consultorio y consentimiento obligatorio de *Habeas Data*.
5. **Dashboard en Tarjetas (Cards):** Eliminado el FullCalendar innecesario del paciente y sustituido por tarjetas de diseño prémium.

### 🅱️ Módulo de Recepción (`recepcionista_dashboard.html`)
1. **Filtro de Citas en Tiempo Real:** Barra superior que permite filtrar simultáneamente el FullCalendar y la Tabla por **Médico Especialista** o por **Cédula / Nombre del Paciente**.
2. **Acciones Presenciales Directas:**
   - **`✓ Asistió` (Botón Verde):** Marca la llegada del paciente y cambia su estado a `En Sala`.
   - **`✗ No Asistió` (Botón Rojo):** Registra la falta manualmente.
3. **Verificación de Tolerancia de 15 Minutos:** Al abrir el panel, el sistema escanea y convierte las citas atrasadas en `No Asistió`.

---

## 🔐 4. Credenciales de Prueba para el Equipo

Todas las cuentas tienen la contraseña estandarizada en: **`admin123`**

- **Administrador:** `admin@pulsia.com`
- **Recepcionista:** `recepcion@pulsia.com`
- **Especialista (Cardiología):** `cardiologia@pulsia.com`
- **Especialista (General):** `medico@pulsia.com`
- **Paciente:** `paciente1@pulsia.com`

---

## 🛠️ 5. Comando de Inasistencias Automáticas

Para ejecutar la verificación de inasistencias en segundo plano o mediante un *Cron Job* del servidor:

```bash
python manage.py marcar_inasistencias
```

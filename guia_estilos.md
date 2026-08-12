# 🎨 Guía de Estilos y Sistema de Diseño (Pulsia Medical Systems)

Este documento establece las directrices visuales, colores, tipografía, componentes y patrones de diseño utilizados en la aplicación **Pulsia**, basados en el **Design System de Stitch MCP** ("Quiet Authority").

---

## 🎨 1. Paleta de Colores

La paleta adopta un enfoque corporativo-clínico refinado, reduciendo la saturación para evitar fatiga visual durante jornadas laborales extensas.

| Token de Color | Valor Hex | Uso Principal |
| :--- | :--- | :--- |
| **`primary`** | `#123748` | Títulos principales de módulo, navegación superior y botones principales. |
| **`primary-container`** | `#2C4E60` | Fondo de tarjetas primarias, estado activo de la barra de navegación superior. |
| **`secondary`** | `#0E6877` | Títulos secundarios, insignias de especialidad y bordes destacados. |
| **`clinical-teal`** | `#0D9488` | Acciones clínicas de alta prioridad (*Check-in*, Agendamiento, Registro, Botón Crear, Día Activo). |
| **`soft-sky`** | `#E0F2FE` | Resaltados de fondo sutiles, degradados suaves y estados hover de tablas. |
| **`surface`** | `#F7F9FB` | Fondo general de la aplicación. |
| **`surface-container-lowest`**| `#FFFFFF` | Fondo de tarjetas, tablas, modales y contenedores elevados. |
| **`success-emerald`** | `#059669` | Estado *Presente* / *Atendida*, confirmación de citas y cuentas activas. |
| **`warning-amber`** | `#D97706` | Advertencias de reprogramación, lista de espera, permisos pendientes y mantenimiento. |
| **`error-red`** | `#BE123C` | Inasistencias (*No-Show*), cancelaciones, cuentas inactivas y bajas de usuario. |

---

## 🔤 2. Tipografía y Fuentes Tipográficas

Utiliza una jerarquía mixta con Google Fonts:

- **Geist (`font-heading`)**: Utilizada en encabezados (`h1`, `h2`, `h3`), etiquetas de estado y botones. Aporta precisión técnica y moderna.
- **Inter (`font-body`)**: Utilizada en párrafos, formularios, notas clínicas e historial. Garantiza máxima legibilidad.

---

## 🏛️ 3. Encabezados de Módulo (Header Cards)

Todos los módulos de la aplicación utilizan un contenedor con **resaltado clínico sutil** (`bg-gradient-to-r from-teal-50/50 via-sky-50/30 to-white`), garantizando que el título se distinga claramente sin parecer un botón interactivo:

- **Contenedor con Resaltado Sutil**: `bg-gradient-to-r from-teal-50/50 via-sky-50/30 to-white p-6 rounded-2xl shadow-sm border border-outline-variant/30 flex flex-col md:flex-row md:items-center justify-between gap-4`.
- **Título de Módulo**: `<h1 class="font-heading text-xl md:text-2xl font-extrabold text-primary">Título del Módulo</h1>` (sin pastillas o cajas que simulen botones).
- **Descripción Acompañante**: `<p class="text-xs text-on-surface-variant mt-1">Texto explicativo breve...</p>`.

---

## 🔍 4. Buscadores y Filtros Automáticos en Tiempo Real

Para maximizar la agilidad administrativa:
- **Filtrado Automático**: Los campos de texto filtran al escribir mediante el helper `oninput="autoSubmitFormDebounced(this.form)"`. Los desplegables `<select>` filtran automáticamente al cambiar de opción (`onchange="this.form.submit()"`).
- **Alineación Vertical del Icono de Lupa**: Todos los inputs de búsqueda encierran la lupa con `relative flex items-center` y la etiqueta `<span class="material-symbols-outlined absolute left-3 text-gray-400 text-lg pointer-events-none">search</span>`, garantizando un centrado vertical 100% perfecto.
- **Botón "Limpiar Filtros"**: En lugar de un botón tradicional de "Buscar", se ofrece un botón/enlace de **Limpiar Filtros** (`restart_alt` icon, `bg-slate-100 hover:bg-slate-200`) que reinicia todos los campos con un solo clic.

---

## ⚡ 5. Renderizado SSR de Pestañas (Cero Parpadeos)

En módulos con pestañas o submódulos (como *Estructura Médica*):
- Las clases `hidden` y los estados activos de los botones se evalúan directamente en el servidor mediante plantillas de Django (`{% if tab == 'cons' %}`).
- Esto garantiza que el navegador reciba y pinte la pestaña activa de forma inmediata desde el paquete HTML inicial, eliminando cualquier parpadeo (*flicker*) o retraso por JavaScript.

---

## 🔘 6. Botones de Acción en Tablas (Icon Action Buttons)

Las acciones por fila en las tablas administrativas emplean botones de icono compactos de 32x32px (`w-8 h-8 rounded-xl`) con feedback táctil (hover) y tooltip flotante nativo (`title="..."`):

- **Ver Detalle**: `bg-teal-50 text-teal-700 hover:bg-teal-600 hover:text-white` con icono `visibility` y `title="Ver Detalle"`.
- **Editar**: `bg-sky-50 text-sky-700 hover:bg-sky-600 hover:text-white` con icono `edit` y `title="Editar..."`.
- **Eliminar / Dar de Baja**: `bg-rose-50 text-rose-700 hover:bg-rose-600 hover:text-white` con icono `person_remove` o `delete` y `title="Dar de baja / Eliminar"`.
- **Reasignar Consultorio / Asignación**: `bg-teal-50 text-teal-700 hover:bg-teal-600 hover:text-white` con icono `assignment_ind` y `title="Reasignar Consultorio"`.
- **Configurar Horario Laboral**: `bg-sky-50 text-sky-700 hover:bg-sky-600 hover:text-white` con icono `edit_calendar` y `title="Configurar Horario Laboral"`.

---

## 📅 7. Calendario e Interacciones Dashboard

- **Navegación Fluida**: Transiciones suaves entre la vista mensual de FullCalendar y la vista detallada por día.
- **Carrusel de Días**: Estructurado en una grilla exacta de 7 columnas (`grid grid-cols-7 gap-2 w-full overflow-hidden`), evitando barras de desplazamiento horizontal.
- **Día Seleccionado**: Resaltado en tono teal clínico (`bg-clinical-teal text-white border-clinical-teal shadow-md`) sin distorsionar el diseño o escalar fuera del contenedor.
- **Cápsulas de Citas (Borde Fuerte + Fondo Suave)**: En todas las vistas del calendario (Mes, Semana, Día) y para todos los roles, las citas se renderizan en cápsulas con **borde sólido (2px) y fondo suave pastel** con texto oscuro de alta legibilidad:
  - **Programada**: `bg-sky-50 border-2 border-sky-700 text-sky-950`
  - **En Sala**: `bg-teal-50 border-2 border-teal-700 text-teal-950`
  - **Atendida**: `bg-emerald-50 border-2 border-emerald-700 text-emerald-950`
  - **No Asistió**: `bg-rose-50 border-2 border-rose-700 text-rose-950`
  - **Pendiente Reubicación**: `bg-amber-50 border-2 border-amber-700 text-amber-950`
  - **Cancelada**: `bg-gray-100 border-2 border-gray-600 text-gray-800`


---

## 🔝 8. Navegación Superior y Submenú de Perfil

- **Ítem Activo**: Resaltado dinámicamente según la ruta (`bg-primary-container text-white font-bold`).
- **Nombres Limpios**: Sin códigos entre paréntesis (como `(HU04)` o `(RN08)`).
- **Submenú de Perfil de Usuario (Derecha)**: Botón con la inicial del usuario, nombre completo y rol. Al hacer clic, despliega un menú flotante interactivamente con la opción **Cerrar Sesión**.

---

## 🚫 9. Prohibición Estricta de Códigos Técnicos en la Interfaz (No HU / RN en UI)

- **Nombres Limpios y Profesionales**: NINGÚN elemento de la interfaz de usuario (botones, encabezados, pastillas, títulos de tarjeta, modales, tablas o textos de ayuda) debe mostrar códigos internos de requerimientos entre paréntesis o sufijos como `(HU01)`, `(HU11)`, `(HU14)`, `(RN05)`, `(RN08)`, etc.
- **Formato Estándar de Encabezado**: Los títulos de módulo deben ser limpios y elegantes: `<h1 class="font-heading text-xl md:text-2xl font-extrabold text-primary">Título del Módulo</h1>` sin etiquetas o insignias que muestren códigos `(HUxx)`.
- **Uso Exclusivo**: Los códigos de historias de usuario y reglas de negocio pertenecen estrictamente al código fuente (docstrings, comentarios) o documentación técnica markdown, nunca a la interfaz visual que ven los usuarios del sistema médico.

---

## 🕒 10. Rango de Horarios y Presentación de Días Festivos en Calendario

- **Rango de Horarios Visibles en Parrilla**: Las vistas de semana (`timeGridWeek`) y día (`timeGridDay`) del calendario muestran el rango visible de **07:00 AM a 06:00 PM** (`slotMinTime: '07:00:00'` y `slotMaxTime: '18:00:00'`). Esto brinda un margen visual de respiración entre el encabezado superior y las citas de las 08:00 AM, permitiendo además visualizar con precisión el límite de cierre de la jornada de las 05:00 PM (17:00).
- **Fila "Citas Totales" (`allDay`)**: La fila superior "Citas Totales" muestra en días ordinarios el conteo total de consultas programadas (ej. `3 Citas`) y en días festivos la pastilla destacada con el nombre oficial del festivo en Colombia (ej. `🇨🇴 Festivo: Batalla de Boyacá`).
- **Resaltado de Colores Nativos**:
  - 🍏 **Día Actual (Hoy)**: Fondo en **verde biche suave** (`#DCFCE7`).
  - 🟠 **Días Festivos Oficiales**: Fondo en **naranja suave** (`#FFEDD5` con borde `#F97316`).



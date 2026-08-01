# 📋 Flujo de Agendamiento de Citas Web - 4 Pasos

## Descripción General
Sistema de agendamiento de citas médicas con barra de progreso visual que guía al paciente a través de 4 pasos claramente definidos.

## 🎯 Flujo de Usuario

### PASO 1: Seleccionar Fecha
- **Vista**: Calendario interactivo mensual
- **Funcionalidad**:
  - Navegación entre meses (anterior/siguiente)
  - Selección de fecha disponible
  - Visualización de fecha seleccionada
  - Deshabilitación de fechas pasadas
- **Acción**: Click en "Continuar" → Avanza a Paso 2
- **Progreso**: Barra muestra "PASO 1 completado"

### PASO 2: Explorar Especialidades
- **Vista**: Cuadrícula de especialidades médicas
- **Funcionalidad**:
  - Tarjetas con iconos de especialidades
  - Selección de especialidad deseada
  - Hover effects para mejor UX
- **Acción**: Click en especialidad + "Continuar" → Avanza a Paso 3
- **Progreso**: Barra muestra "PASO 2 completado"

### PASO 3: Buscar Especialista
- **Vista**: Lista de especialistas disponibles
- **Funcionalidad**:
  - Barra de búsqueda por nombre
  - Filtro en tiempo real
  - Tarjetas de perfil de especialistas con:
    - Nombre del médico
    - Especialidad
    - Calificación (rating)
    - Disponibilidad
- **Acción**: Click en "Seleccionar" + "Continuar" → Avanza a Paso 4
- **Progreso**: Barra muestra "PASO 3 completado"

### PASO 4: Confirmación de Cita
- **Vista**: Pantalla de resumen y confirmación
- **Funcionalidad**:
  - Resumen completo de la cita:
    - Médico seleccionado
    - Especialidad
    - Fecha y hora
    - Ubicación
  - Animación de éxito (checkmark)
- **Acciones**:
  - **"Confirmar y Agendar"**: Envía el formulario y crea la cita en la BD
  - **"Cancelar"**: Regresa al dashboard del paciente
- **Progreso**: Barra muestra "PASO 4 - Confirmación"

## 🎨 Componentes Visuales

### Barra de Progreso
```
[1] ━━━ [2] ━━━ [3] ━━━ [4]
```
- **Estados**:
  - `active`: Paso actual (azul brillante)
  - `completed`: Paso completado (azul oscuro)
  - `pending`: Paso pendiente (gris)

### Botones de Navegación
- **"Anterior"**: Permite retroceder al paso previo
- **"Continuar"**: Avanza al siguiente paso (deshabilitado hasta completar selección)
- **"Cancelar"**: Regresa al dashboard en cualquier momento

## 🔧 Implementación Técnica

### Archivos Creados/Modificados

#### 1. Template Principal
**Archivo**: `agendamiento/templates/agendamiento/paciente/agendar_cita_web.html`
- Integra las 4 interfaces de Stitch en un flujo cohesivo
- JavaScript para navegación entre pasos
- Sistema de validación de selecciones
- Formulario final que envía datos al backend

#### 2. Vista (View)
**Archivo**: `agendamiento/views/dashboard_views.py`
- Función: `paciente_agendar_cita_web_view()`
- Carga datos de especialidades y especialistas
- Renderiza el template con contexto necesario

#### 3. URL Routing
**Archivo**: `agendamiento/urls.py`
- Ruta: `/paciente/agendar-cita-web/`
- Nombre: `paciente_agendar_cita_web`

#### 4. Dashboard del Paciente
**Archivo**: `agendamiento/templates/agendamiento/dashboard/paciente_dashboard.html`
- Botón "Agendar Cita Web" actualizado
- Redirección al nuevo flujo

## 📊 Flujo de Datos

```
Dashboard Paciente
       ↓
[Botón: Agendar Cita Web]
       ↓
paciente_agendar_cita_web_view()
       ↓
Renderiza: agendar_cita_web.html
       ↓
[Usuario completa 4 pasos]
       ↓
[Submit formulario]
       ↓
paciente_agendar_view() (POST)
       ↓
agendar_cita_web() [service]
       ↓
Crea Cita en BD
       ↓
Redirect → Dashboard Paciente
```

## 🚀 Cómo Usar

### Para Pacientes:
1. Iniciar sesión como paciente
2. En el dashboard, click en "Agendar Cita Web"
3. Seguir los 4 pasos guiados por la barra de progreso
4. Confirmar la cita en el paso final

### Para Desarrolladores:
1. Asegurarse de tener especialidades y especialistas en la BD
2. Acceder a: `http://localhost:8000/paciente/agendar-cita-web/`
3. El flujo valida que el usuario sea de tipo PACIENTE

## ✅ Reglas de Negocio Aplicadas

- **RN01**: Límite de reprogramación (aplicado en otro módulo)
- **RN02**: Anticipación de 24 horas (aplicado en otro módulo)
- **RN04**: Penalización por inasistencia (verifica antes de permitir acceso)
- **Habeas Data**: Aceptación automática en el formulario final

## 🎯 Historias de Usuario Cumplidas

- **HU02**: Agendamiento Web Autónomo ✅
  - Calendario interactivo con disponibilidad
  - Filtro por especialidad y especialista
  - Aceptación de tratamiento de datos
  - Reserva almacenada con estado "Programada"

## 🔄 Mejoras Futuras

1. Integración con API de festivos (Ley Emiliani)
2. Validación de horarios de descanso en tiempo real
3. Mostrar disponibilidad real de cada especialista
4. Selector de hora en el Paso 1
5. Filtros adicionales en Paso 2 (búsqueda de especialidades)
6. Opción de añadir a calendario (Google Calendar, iCal)
7. Confirmación por email automática
8. Animaciones más fluidas entre transiciones

## 📝 Notas Adicionales

- El diseño sigue el sistema de diseño Material 3
- Totalmente responsive (mobile-first)
- Colores y tokens de diseño consistentes con Pulsia
- Las interfaces base provienen de Stitch (diseño pre-aprobado)

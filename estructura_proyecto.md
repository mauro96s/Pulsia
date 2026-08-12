# Estructura del Proyecto Pulsia (Arquitectura MVC + Service Layer)

Este documento centraliza la arquitectura de directorios y la organización modular del proyecto **Pulsia**, diseñado bajo la arquitectura MVC (Model-View-Controller) extendida con una capa de servicios (Service Layer).

---

## 📐 Árbol de Directorios del Proyecto

```text
Pulsia/
│
├── config/                       # ⚙️ Configuración Global del Proyecto Django
│   ├── settings.py               # Ajustado con environ, SQLite/PostgreSQL, apps e idiomas
│   ├── urls.py                   # Enrutador principal del sitio
│   ├── wsgi.py / asgi.py
│   └── __init__.py
│
├── agendamiento/                 # 🏥 Aplicación Principal Unificada
│   ├── __init__.py
│   ├── apps.py
│   ├── admin.py                  # Registro completo de modelos para el panel de administración
│   ├── urls.py                   # Enrutador interno de agendamiento (/administracion/...)
│   │
│   ├── models/                   # 🗄️ MODELOS (La "M" en MVC - Modularizados)
│   │   ├── __init__.py           # Re-exporta todos los modelos para fácil acceso
│   │   ├── usuarios.py           # CustomUser (AbstractUser), RolUsuario (ENUM)
│   │   ├── pacientes.py          # Paciente (Perfil, Habeas Data, Inasistencias)
│   │   ├── especialistas.py      # Especialidad, Consultorio, Especialista (con consultorio FK), HorarioLaboral
│   │   └── citas.py              # Cita, AusenciasPermisos, EstadoCita, EstadoAprobacion
│   │
│   ├── views/                    # 🎮 CONTROLADORES / VISTAS (La "C" en MVC)
│   │   ├── __init__.py           # Re-exporta todas las vistas
│   │   ├── auth_views.py         # Login, Logout, Gestión de sesión (HU01, RN07)
│   │   ├── dashboard_views.py    # Redirección y tableros según el rol de usuario
│   │   ├── admin_views.py        # Gestión de Usuarios, Estructura Médica, Aprobación de Permisos
│   │   ├── citas_views.py        # Agendamiento web, reprogramación y vista de recepción
│   │   ├── pacientes_views.py    # Historial clínico y notas de atención (HU05)
│   │   ├── especialistas_views.py# Check-in de turno y solicitudes de ausencia (HU04, HU13)
│   │   └── reportes_views.py     # Tableros BI y métricas administrativas (HU11)
│   │
│   ├── services/                 # ⚙️ LÓGICA DE NEGOCIO Y REGLAS (Service Layer)
│   │   ├── __init__.py
│   │   ├── citas_service.py      # Validaciones de reprogramación (RN01, RN02) e inasistencias (RN03, RN04)
│   │   ├── ausencias_service.py  # Lógica de ausencias médicas y bloqueos (RN05, RN08, HU14)
│   │   ├── festivos_service.py   # Consumo de API externa de festivos Ley Emiliani (HU08)
│   │   └── notificaciones_service.py # Envío automático de correos (HU10)
│   │
│   ├── migrations/               # 📦 Migraciones del ORM de Django
│   │   ├── 0001_initial.py       # Migración inicial que crea los modelos base
│   │   ├── 0002_...              # Ajustes y actualizaciones de campos
│   │   ├── 0003_especialista_consultorio.py # Relación ForeignKey Especialista <-> Consultorio
│   │   └── __init__.py
│   │
│   └── templates/                # 🎨 VISTAS E INTERFAZ (La "V" en MVC)
│       └── agendamiento/
│           ├── base.html         # Plantilla maestra con Tailwind CSS y menú por rol
│           ├── auth/             # login.html, register.html
│           ├── dashboard/        # admin.html, recepcion.html, especialista.html, paciente.html
│           ├── admin/            # usuarios.html, estructura_medica.html, permisos.html
│           ├── citas/            # agendar.html, mis_citas.html, agenda_global.html
│           ├── pacientes/        # historial_clinico.html
│           ├── especialistas/    # mi_agenda.html, solicitar_permiso.html
│           └── reportes/         # reportes_bi.html
│
├── static/                       # 📁 Recursos estáticos globales (CSS, JS, Imágenes)
│   ├── css/
│   ├── js/                       # pulsia_calendar.js (FullCalendar + carrusel interactivo)
│   └── img/
│
├── .env                          # 🔒 Variables de entorno locales (DB, Secret Keys - IGNORADO POR GIT)
├── .env.example                  # 📄 Plantilla de variables de entorno para colaboradores
├── .gitignore                    # 🛡️ Protección de credenciales y entornos virtuales
├── manage.py                     # 🛠️ Ejecutable de comandos de Django
├── guia_estilos.md               # 🎨 Guía de estilos y sistema de diseño visual de Pulsia
├── estructura_proyecto.md       # 📐 Documentación de arquitectura de directorios
└── requirements.txt              # 📦 Dependencias de Python del proyecto
```

---

## 🗄️ Mapeo del Esquema Relacional a los Modelos ORM

| Entidad / Tabla | Modelo en Django | Archivo | Descripción |
| :--- | :--- | :--- | :--- |
| `usuarios` | `CustomUser` | `agendamiento/models/usuarios.py` | Usuario base con rol (Administrador, Especialista, Recepcionista, Paciente). |
| `pacientes` | `Paciente` | `agendamiento/models/pacientes.py` | Perfil de paciente (Habeas Data, Inasistencias, Fecha Nacimiento). |
| `especialidades` | `Especialidad` | `agendamiento/models/especialistas.py` | Catálogo de especialidades clínicas. |
| `consultorios` | `Consultorio` | `agendamiento/models/especialistas.py` | Infraestructura de consultorios físicos. |
| `especialistas` | `Especialista` | `agendamiento/models/especialistas.py` | Perfil médico vinculado a Especialidad y Consultorio (FK). |
| `horarios_laborales` | `HorarioLaboral` | `agendamiento/models/especialistas.py` | Configuración de turnos y franjas de descanso por especialista. |
| `citas` | `Cita` | `agendamiento/models/citas.py` | Citas médicas y estados (*Programada, En Sala, Atendida, Cancelada, No Asistió*). |
| `ausencias_permisos` | `AusenciasPermisos` | `agendamiento/models/citas.py` | Solicitudes y aprobaciones de ausencias/permisos médicos. |

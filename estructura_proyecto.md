# Estructura del Proyecto Pulsia (MVT)

A continuación, se detalla la estructura de directorios y archivos de la arquitectura MVT (Model-View-Template) que se ha diseñado para el Sistema de Agendamiento Médico.

```text
Pulsia/
│
├── config/                       # ⚙️ CONFIGURACIÓN GLOBAL (El Proyecto en sí)
│   ├── settings.py               # Configuración general, conexión a PostgreSQL, apps instaladas.
│   ├── urls.py                   # Enrutador principal. Conecta las URLs de cada aplicación.
│   ├── wsgi.py / asgi.py         # Archivos para cuando despliegues a producción.
│   └── __init__.py
│
├── usuarios/                     # 👥 APP 1: Identidad y Roles (Módulo de Autenticación)
│   ├── models.py                 # [M] Modelo 'CustomUser' (extiende AbstractUser), 'Paciente' y 'Especialista'.
│   ├── views.py                  # [V] Lógica de Login, Logout y redirección según rol (HU01).
│   ├── urls.py                   # Rutas web exclusivas para autenticación (ej: /login/).
│   ├── admin.py                  # Registro de modelos en el panel de administrador por defecto.
│   └── forms.py                  # Formularios para login y actualización de datos de perfil.
│
├── clinica/                      # 🏥 APP 2: Configuración del Centro Médico
│   ├── models.py                 # [M] Modelos 'Especialidad', 'Consultorio' y 'HorarioLaboral'.
│   ├── views.py                  # [V] CRUD de especialidades/consultorios (HU12) y Reportes BI (HU11).
│   ├── urls.py                   # Rutas web administrativas (ej: /clinica/consultorios/).
│   └── services.py               # (Recomendado) Archivo extra para consultar la API de Festivos (HU08).
│
├── citas/                        # 📅 APP 3: Corazón del Negocio (Agendamiento)
│   ├── models.py                 # [M] Modelos 'Cita' y 'AusenciasPermisos'.
│   ├── views.py                  # [V] Lógica pesada: Agendamiento web (HU02), Reprogramación (HU03), Check-in (HU13).
│   ├── urls.py                   # Rutas para el paciente, médico y recepción (ej: /citas/agendar/).
│   ├── forms.py                  # Formularios para agendar, solicitar permisos y notas clínicas (HU05).
│   └── utils.py                  # (Recomendado) Funciones para envío de notificaciones automáticas (HU10).
│
├── templates/                    # 🎨 LA "T" DE MVT: Plantillas y Vistas para el Usuario
│   ├── base.html                 # Plantilla maestra. Aquí va tu CDN de TailwindCSS, el menú principal y el footer.
│   ├── auth/                     
│   │   └── login.html            # Pantalla de inicio de sesión segura.
│   ├── paciente/                 
│   │   ├── agendar_cita.html     # Calendario interactivo de disponibilidad.
│   │   └── mis_citas.html        # Lista de citas con botones de reprogramar/cancelar.
│   ├── especialista/             
│   │   ├── mi_agenda.html        # Vista diaria del médico con botón "Iniciar Turno".
│   │   └── notas_clinicas.html   # Formulario para escribir sobre la cita atendida.
│   ├── recepcion/                
│   │   └── agenda_global.html    # El calendario maestro sin restricciones de tiempo.
│   └── admin/                    
│       └── dashboard_bi.html     # Gráficos y reportes de inasistencias.
│
├── static/                       # 📁 ARCHIVOS ESTÁTICOS (Recursos públicos)
│   ├── css/                      # Hojas de estilo extra (si necesitas algo fuera de Tailwind).
│   ├── js/                       # Scripts para alertas interactivas o lógica del calendario frontend.
│   └── img/                      # Logos de la clínica, avatares, iconos.
│
├── manage.py                     # 🛠️ Script nativo de Django para correr servidor, migraciones, etc.
├── pulsia.sql                    # Script original de base de datos (PostgreSQL).
├── HU_RN.md                      # Documento de Historias de Usuario y Reglas de Negocio.
└── requirements.txt              # Lista de dependencias del proyecto.
```

### Notas Adicionales:
* **Separación de Responsabilidades:** No sobrecargues `views.py`. Usa archivos como `services.py` o `utils.py` para lógica externa (como enviar correos o conectarse a APIs).
* **Base de Datos:** Al usar PostgreSQL, los modelos deben tener en cuenta que las migraciones generarán las tablas con integridad referencial nativa.
* **Seguridad:** Los roles se manejarán mediante decoradores y validaciones tanto en Frontend (Templates) como en Backend (Vistas).

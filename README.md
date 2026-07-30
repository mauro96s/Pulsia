# 🏥 Pulsia - Sistema de Gestión y Agendamiento de Citas Médicas

Bienvenido al repositorio oficial del proyecto **Pulsia**. Este sistema permite la gestión integral de citas médicas de consulta externa, control de horarios, ausencias de especialistas, penalización por inasistencias y reportes administrativos.

Desarrollado en **Python (Django)** con **PostgreSQL** mediante una arquitectura **MVC + Service Layer**.

---

## 🚀 Guía de Instalación y Configuración Paso a Paso

Sigue estas instrucciones detenidamente para clonar y ejecutar el proyecto en tu máquina local.

---

### 📋 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado en tu computadora:
- **Python 3.10+** (Verificar con `python --version`)
- **PostgreSQL 14+** y un gestor como **pgAdmin** o **DBeaver**.
- **Git** (Verificar con `git --version`)

---

### 1️⃣ Clonar el Repositorio

Abre la terminal en la carpeta donde deseas guardar el proyecto y ejecuta:

```bash
git clone https://github.com/mauro96s/Pulsia.git
cd Pulsia
```

---

### 2️⃣ Crear y Activar el Entorno Virtual (`venv`)

Es indispensable aislar las dependencias del proyecto utilizando un entorno virtual.

* **En Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\activate
  ```

* **En Linux / macOS:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

> 💡 **Nota:** Sabrás que el entorno está activo porque aparecerá `(venv)` al inicio de la línea de comandos.

---

### 3️⃣ Instalar Dependencias

Con el entorno virtual activo, instala todas las librerías necesarias ejecutando:

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Configurar las Variables de Entorno (`.env`)

Por motivos de seguridad, las contraseñas y claves privadas no se suben al repositorio. Debes crear tu propio archivo `.env` basado en la plantilla de ejemplo:

1. Duplica o renombra el archivo `.env.example` a `.env`:
   * **Windows:** `copy .env.example .env`
   * **Linux/Mac:** `cp .env.example .env`

2. Abre el archivo `.env` y edita los valores con las credenciales de tu servidor PostgreSQL local:

```env
# Base de Datos PostgreSQL
DB_NAME=pulsia_db
DB_USER=tu_usuario_postgres
DB_PASSWORD=tu_contraseña_postgres
DB_HOST=127.0.0.1
DB_PORT=5432

# Seguridad de Django
SECRET_KEY=django-insecure-clave-secreta-para-desarrollo
DEBUG=True
```

---

### 5️⃣ Crear la Base de Datos en PostgreSQL

Antes de ejecutar las migraciones, debes asegurarte de que la base de datos especificada en `DB_NAME` exista en tu PostgreSQL.

* Abre **pgAdmin** o la consola de PostgreSQL (`psql`) y crea la base de datos:
  ```sql
  CREATE DATABASE pulsia_db;
  ```

---

### 6️⃣ Ejecutar Migraciones de la Base de Datos

Con la base de datos creada y las credenciales en tu `.env`, ejecuta el comando para construir las 8 tablas requeridas:

```bash
python manage.py migrate
```

> ✅ Verás un listado de confirmaciones con estado `OK` indicando que todas las tablas y relaciones fueron creadas exitosamente.

---

### 7️⃣ Crear el Usuario Administrador (Superusuario)

Para poder ingresar al panel administrativo de Django (`/admin`) y probar las funcionalidades con permisos completos:

```bash
python manage.py createsuperuser
```

Ingresa los datos solicitados:
* **Correo electrónico:** (Ej: `admin@pulsia.com`)
* **Nombre Completo:** (Ej: `Administrador General`)
* **Rol:** `Administrador`
* **Contraseña:** (Escribe tu clave deseada; los caracteres no se mostrarán por seguridad).

---

### 8️⃣ Iniciar el Servidor de Desarrollo

¡Todo está listo! Ejecuta el servidor local:

```bash
python manage.py runserver
```

Abre tu navegador e ingresa a:
* **Aplicación Web:** `http://127.0.0.1:8000/`
* **Panel de Administración:** `http://127.0.0.1:8000/admin/`

---

## 🛠️ Comandos Frecuentes

| Acción | Comando |
| :--- | :--- |
| **Activar entorno (Windows)** | `.\venv\Scripts\activate` |
| **Activar entorno (Linux/Mac)** | `source venv/bin/activate` |
| **Correr servidor** | `python manage.py runserver` |
| **Crear nueva migración** | `python manage.py makemigrations` |
| **Aplicar migraciones** | `python manage.py migrate` |
| **Verificar salud del sistema** | `python manage.py check` |

---

## 📁 Documentación Adicional

* [HU_RN.md](HU_RN.md): Historias de Usuario (14 HU) y Reglas de Negocio (RN01 - RN08).
* [estructura_proyecto.md](estructura_proyecto.md): Explicación detallada de la arquitectura MVC + Service Layer.
* [pulsia.sql](pulsia.sql): Esquema relacional SQL de referencia.

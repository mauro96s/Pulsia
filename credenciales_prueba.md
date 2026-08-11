# Credenciales de Prueba — Pulsia Medical Systems

> **Contraseña universal para todos los usuarios:** `123456`
>
> **Hash (PBKDF2-SHA256, Django):**
> `pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=`

---

## Instrucciones de Carga

1. Asegúrate de haber corrido `python manage.py migrate` antes de ejecutar el script.
2. Ejecuta el archivo **`pulsia_datos_prueba.sql`** en pgAdmin o psql:
   ```sql
   \i ruta/al/pulsia_datos_prueba.sql
   ```
3. El script hace borrado en cascada de datos previos y reinicia las secuencias automáticamente.

---

## Administrador (1)

| Nombre       | Correo / Username    | Contraseña | Num. Doc   | Dashboard             |
| :----------- | :------------------- | :--------- | :--------- | :-------------------- |
| Ana Diaz     | `andi@pulsia.com`    | `123456`   | 1001001001 | `/dashboard/admin/`   |

---

## Recepcionistas (2)

| Nombre       | Correo / Username    | Contraseña | Num. Doc   |
| :----------- | :------------------- | :--------- | :--------- |
| Rosa Castro  | `roca@pulsia.com`    | `123456`   | 1002002002 |
| Luis Garcia  | `luga@pulsia.com`    | `123456`   | 1002002003 |

---

## Especialistas (21) — 3 por especialidad

### Medicina General

| Nombre          | Correo               | Turno    | Consultorio | Días            |
| :-------------- | :------------------- | :------- | :---------- | :-------------- |
| Carlos Parra    | `cape@pulsia.com`    | Mañana   | MG-101      | Lun – Vie       |
| Maria Rodriguez | `maro@pulsia.com`    | Tarde    | MG-102      | Lun – Vie       |
| Jimmy Mejia     | `jime@pulsia.com`    | Completo | MG-103      | Lun – Sáb       |

### Odontología

| Nombre          | Correo               | Turno    | Consultorio | Días            |
| :-------------- | :------------------- | :------- | :---------- | :-------------- |
| Sandra Torres   | `sato@pulsia.com`    | Mañana   | OD-201      | Lun–Jue + Sáb  |
| Felipe Vargas   | `feva@pulsia.com`    | Tarde    | OD-202      | Mar – Vie       |
| Valentina Leon  | `vale@pulsia.com`    | Completo | OD-203      | Lun – Vie       |

### Cardiología

| Nombre          | Correo               | Turno    | Consultorio | Días            |
| :-------------- | :------------------- | :------- | :---------- | :-------------- |
| Andres Soto     | `anso@pulsia.com`    | Mañana   | CA-301      | Lun – Mié       |
| Claudia Munoz   | `clmu@pulsia.com`    | Tarde    | CA-302      | Jue–Vie + Sáb  |
| Ricardo Castro  | `rica@pulsia.com`    | Completo | CA-303      | Lun – Vie       |

### Pediatría

| Nombre          | Correo               | Turno    | Consultorio | Días            |
| :-------------- | :------------------- | :------- | :---------- | :-------------- |
| Lucia Bermudez  | `lube@pulsia.com`    | Mañana   | PE-401      | Lun – Vie       |
| Daniel Gomez    | `dago@pulsia.com`    | Tarde    | PE-402      | Lun – Jue       |
| Paula Ramirez   | `para@pulsia.com`    | Completo | PE-403      | Lun – Sáb       |

### Ginecología

| Nombre          | Correo               | Turno    | Consultorio | Días            |
| :-------------- | :------------------- | :------- | :---------- | :-------------- |
| Camila Morales  | `camo@pulsia.com`    | Mañana   | GI-501      | Lun – Vie       |
| Sofia Rios      | `sori@pulsia.com`    | Tarde    | GI-502      | Mar–Vie + Sáb  |
| Nicolas Olarte  | `niol@pulsia.com`    | Completo | GI-503      | Mié – Vie       |

### Dermatología

| Nombre          | Correo               | Turno    | Consultorio | Días            |
| :-------------- | :------------------- | :------- | :---------- | :-------------- |
| Isabel Pena     | `ispe@pulsia.com`    | Mañana   | DE-601      | Lun – Jue       |
| Hernan Ramos    | `hera@pulsia.com`    | Tarde    | DE-602      | Lun – Vie       |
| Nives Villa     | `nivi@pulsia.com`    | Completo | DE-603      | Lun – Sáb       |

### Psicología

| Nombre            | Correo               | Turno    | Consultorio | Días            |
| :---------------- | :------------------- | :------- | :---------- | :-------------- |
| Alejandro Cordoba | `alco@pulsia.com`    | Mañana   | PS-701      | Lun – Vie       |
| Gustavo Salcedo   | `gusa@pulsia.com`    | Tarde    | PS-702      | Lun–Jue + Sáb  |
| Angela Guerrero   | `angu@pulsia.com`    | Completo | PS-703      | Mar – Vie       |

---

## Pacientes (100) — Muestra representativa

| Nombre           | Correo                    | Contraseña | Num. Doc   |
| :--------------- | :------------------------ | :--------- | :--------- |
| Pedro Martinez   | `pema@pulsia.com`         | `123456`   | 1004004004 |
| Carlos Luna      | `luna001@pulsia.com`      | `123456`   | 1004000002 |
| Maria Meza       | `meza002@pulsia.com`      | `123456`   | 1004000003 |
| Juan Sosa        | `sosa003@pulsia.com`      | `123456`   | 1004000004 |
| Ana Vega         | `vega004@pulsia.com`      | `123456`   | 1004000005 |
| Laura Rios       | `rios005@pulsia.com`      | `123456`   | 1004000006 |
| Diego Nino       | `nino006@pulsia.com`      | `123456`   | 1004000007 |
| Paula Ruiz       | `ruiz007@pulsia.com`      | `123456`   | 1004000008 |
| Jorge Alba       | `alba008@pulsia.com`      | `123456`   | 1004000009 |
| Lucia Mora       | `mora009@pulsia.com`      | `123456`   | 1004000010 |

> Los 90 pacientes restantes siguen el patrón: `[apellido][N]@pulsia.com` con num. doc desde `1004000011` hasta `1004000100`.
> El patrón de correos completo está en el archivo `pulsia_datos_prueba.sql`.

---

## Lógica de Autenticación y Registro

1. **Redirección por Rol en Login (`/login/`)**: Al iniciar sesión, el sistema valida la contraseña hash en PostgreSQL, recupera el atributo `rol` del modelo `CustomUser` y redirige al tablero correspondiente.
2. **Registro Autónomo Exclusivo de Pacientes (`/register/`)**: El formulario público asigna automáticamente el rol `Paciente`.
3. Los roles **Administrador**, **Recepcionista** y **Especialista** son gestionados únicamente desde el panel del Administrador.

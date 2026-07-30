-- =========================================================
-- 1. CREACIÓN DE TIPOS PERSONALIZADOS (ENUM)
-- =========================================================

CREATE TYPE rol_usuario AS ENUM (
    'Administrador', 'Recepcionista', 'Especialista', 'Paciente'
);

CREATE TYPE estado_turno_enum AS ENUM (
    'Presente', 'Ausente'
);

CREATE TYPE estado_cita_enum AS ENUM (
    'Programada', 'En_Sala', 'Atendida', 'Cancelada', 'No_Asistio', 'Pendiente_Reubicacion'
);

CREATE TYPE estado_aprobacion_enum AS ENUM (
    'Pendiente', 'Aprobado', 'Rechazado'
);

-- =========================================================
-- 2. MÓDULO DE AUTENTICACIÓN Y USUARIOS
-- =========================================================

CREATE TABLE usuarios (
    id_usuario SERIAL PRIMARY KEY,
    nombre_completo VARCHAR(150) NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    contrasena_hash VARCHAR(255) NOT NULL,
    rol rol_usuario NOT NULL,
    telefono VARCHAR(20),
    estado_cuenta BOOLEAN DEFAULT TRUE
);

CREATE TABLE pacientes (
    id_paciente SERIAL PRIMARY KEY,
    id_usuario INTEGER NOT NULL REFERENCES usuarios(id_usuario),
    fecha_nacimiento DATE NOT NULL,
    acepta_habeas_data BOOLEAN NOT NULL,
    contador_inasistencias INTEGER DEFAULT 0
);

-- =========================================================
-- 3. MÓDULO MÉDICO Y OPERATIVO
-- =========================================================

CREATE TABLE especialidades (
    id_especialidad SERIAL PRIMARY KEY,
    nombre_especialidad VARCHAR(100) NOT NULL,
    descripcion TEXT
);

CREATE TABLE especialistas (
    id_especialista SERIAL PRIMARY KEY,
    id_usuario INTEGER NOT NULL REFERENCES usuarios(id_usuario),
    id_especialidad INTEGER NOT NULL REFERENCES especialidades(id_especialidad),
    estado_turno estado_turno_enum DEFAULT 'Ausente'
);

CREATE TABLE consultorios (
    id_consultorio SERIAL PRIMARY KEY,
    nombre_codigo VARCHAR(50) UNIQUE NOT NULL,
    estado_operativo BOOLEAN DEFAULT TRUE
);

-- =========================================================
-- 4. MÓDULO DE AGENDAS Y CITAS
-- =========================================================

CREATE TABLE horarios_laborales (
    id_horario SERIAL PRIMARY KEY,
    id_especialista INTEGER NOT NULL REFERENCES especialistas(id_especialista),
    dia_semana INTEGER NOT NULL CHECK (dia_semana BETWEEN 1 AND 7), -- 1 = Lunes, 7 = Domingo
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    hora_inicio_descanso TIME,
    hora_fin_descanso TIME
);

CREATE TABLE citas (
    id_cita SERIAL PRIMARY KEY,
    id_paciente INTEGER NOT NULL REFERENCES pacientes(id_paciente),
    id_especialista INTEGER NOT NULL REFERENCES especialistas(id_especialista),
    id_consultorio INTEGER NOT NULL REFERENCES consultorios(id_consultorio),
    fecha_hora_inicio TIMESTAMP NOT NULL,
    fecha_hora_fin TIMESTAMP NOT NULL,
    estado_cita estado_cita_enum DEFAULT 'Programada',
    contador_reprogramacion INTEGER DEFAULT 0,
    notas_clinicas TEXT
);

-- =========================================================
-- 5. MÓDULO DE EXCEPCIONES Y PERMISOS
-- =========================================================

CREATE TABLE ausencias_permisos (
    id_permiso SERIAL PRIMARY KEY,
    id_especialista INTEGER NOT NULL REFERENCES especialistas(id_especialista),
    fecha_hora_inicio TIMESTAMP NOT NULL,
    fecha_hora_fin TIMESTAMP NOT NULL,
    motivo_solicitud TEXT NOT NULL,
    estado_aprobacion estado_aprobacion_enum DEFAULT 'Pendiente'
);
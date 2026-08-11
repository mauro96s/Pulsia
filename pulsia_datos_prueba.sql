-- =============================================================================
-- PULSIA MEDICAL SYSTEMS — Script de Datos de Prueba
-- Base de Datos: PostgreSQL | Formato: Django ORM (tablas reales)
-- Objetivo: Poblar con datos realistas para demo y QA
-- Generado: Agosto 2026
-- INSTRUCCIONES: ejecutar en psql o pgAdmin contra la base de datos pulsia_db
--   DESPUÉS de haber corrido: python manage.py migrate
-- =============================================================================

-- =============================================================================
-- PASO 1: BORRADO EN CASCADA
-- =============================================================================
DELETE FROM agendamiento_ausenciaspermisos;
DELETE FROM agendamiento_cita;
DELETE FROM agendamiento_horariolaboral;
DELETE FROM agendamiento_especialista;
DELETE FROM agendamiento_paciente;
DELETE FROM agendamiento_especialidad;
DELETE FROM agendamiento_consultorio;
DELETE FROM agendamiento_customuser WHERE username LIKE '%@pulsia.com';

-- =============================================================================
-- PASO 2: REINICIO DE SECUENCIAS
-- =============================================================================
ALTER SEQUENCE agendamiento_ausenciaspermisos_id_seq RESTART WITH 1;
ALTER SEQUENCE agendamiento_cita_id_seq RESTART WITH 1;
ALTER SEQUENCE agendamiento_horariolaboral_id_seq RESTART WITH 1;
ALTER SEQUENCE agendamiento_especialista_id_seq RESTART WITH 1;
ALTER SEQUENCE agendamiento_paciente_id_seq RESTART WITH 1;
ALTER SEQUENCE agendamiento_especialidad_id_seq RESTART WITH 1;
ALTER SEQUENCE agendamiento_consultorio_id_seq RESTART WITH 1;
ALTER SEQUENCE agendamiento_customuser_id_seq
  RESTART WITH 1;
-- Ajustamos la secuencia de usuarios al valor correcto DESPUÉS del borrado,
-- para no colisionar con cualquier superusuario que quede en la tabla.
SELECT setval(
  'agendamiento_customuser_id_seq',
  COALESCE((SELECT MAX(id) FROM agendamiento_customuser), 0) + 1,
  false
);

-- =============================================================================
-- PASO 3: USUARIOS
-- Hash de contrasena 123456: pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=
-- =============================================================================

-- ADMINISTRADOR
INSERT INTO agendamiento_customuser
  (password, last_login, is_superuser, username, first_name, last_name, email,
   is_staff, is_active, date_joined,
   nombre_completo, tipo_documento, num_documento, correo, rol, telefono, estado_cuenta)
VALUES
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=',
   NULL, TRUE, 'andi@pulsia.com', 'Ana', 'Diaz', 'andi@pulsia.com',
   TRUE, TRUE, NOW(),
   'Ana Diaz', 'CC', '1001001001', 'andi@pulsia.com', 'Administrador', '3001000001', TRUE);

-- RECEPCIONISTAS
INSERT INTO agendamiento_customuser
  (password, last_login, is_superuser, username, first_name, last_name, email,
   is_staff, is_active, date_joined,
   nombre_completo, tipo_documento, num_documento, correo, rol, telefono, estado_cuenta)
VALUES
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=',
   NULL, FALSE, 'roca@pulsia.com', 'Rosa', 'Castro', 'roca@pulsia.com',
   FALSE, TRUE, NOW(),
   'Rosa Castro', 'CC', '1002002002', 'roca@pulsia.com', 'Recepcionista', '3002000002', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=',
   NULL, FALSE, 'luga@pulsia.com', 'Luis', 'Garcia', 'luga@pulsia.com',
   FALSE, TRUE, NOW(),
   'Luis Garcia', 'CC', '1002002003', 'luga@pulsia.com', 'Recepcionista', '3002000003', TRUE);

-- ESPECIALISTAS: Medicina General (ESP 1-3)
INSERT INTO agendamiento_customuser
  (password, last_login, is_superuser, username, first_name, last_name, email,
   is_staff, is_active, date_joined,
   nombre_completo, tipo_documento, num_documento, correo, rol, telefono, estado_cuenta)
VALUES
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'cape@pulsia.com', 'Carlos', 'Parra', 'cape@pulsia.com', FALSE, TRUE, NOW(), 'Carlos Parra', 'CC', '1003003003', 'cape@pulsia.com', 'Especialista', '3003000003', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'maro@pulsia.com', 'Maria', 'Rodriguez', 'maro@pulsia.com', FALSE, TRUE, NOW(), 'Maria Rodriguez', 'CC', '1003003004', 'maro@pulsia.com', 'Especialista', '3003000004', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'jime@pulsia.com', 'Jimmy', 'Mejia', 'jime@pulsia.com', FALSE, TRUE, NOW(), 'Jimmy Mejia', 'CC', '1003003005', 'jime@pulsia.com', 'Especialista', '3003000005', TRUE);

-- ESPECIALISTAS: Odontologia (ESP 4-6)
INSERT INTO agendamiento_customuser
  (password, last_login, is_superuser, username, first_name, last_name, email,
   is_staff, is_active, date_joined,
   nombre_completo, tipo_documento, num_documento, correo, rol, telefono, estado_cuenta)
VALUES
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'sato@pulsia.com', 'Sandra', 'Torres', 'sato@pulsia.com', FALSE, TRUE, NOW(), 'Sandra Torres', 'CC', '1003003006', 'sato@pulsia.com', 'Especialista', '3003000006', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'feva@pulsia.com', 'Felipe', 'Vargas', 'feva@pulsia.com', FALSE, TRUE, NOW(), 'Felipe Vargas', 'CC', '1003003007', 'feva@pulsia.com', 'Especialista', '3003000007', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'vale@pulsia.com', 'Valentina', 'Leon', 'vale@pulsia.com', FALSE, TRUE, NOW(), 'Valentina Leon', 'CC', '1003003008', 'vale@pulsia.com', 'Especialista', '3003000008', TRUE);

-- ESPECIALISTAS: Cardiologia (ESP 7-9)
INSERT INTO agendamiento_customuser
  (password, last_login, is_superuser, username, first_name, last_name, email,
   is_staff, is_active, date_joined,
   nombre_completo, tipo_documento, num_documento, correo, rol, telefono, estado_cuenta)
VALUES
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'anso@pulsia.com', 'Andres', 'Soto', 'anso@pulsia.com', FALSE, TRUE, NOW(), 'Andres Soto', 'CC', '1003003009', 'anso@pulsia.com', 'Especialista', '3003000009', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'clmu@pulsia.com', 'Claudia', 'Munoz', 'clmu@pulsia.com', FALSE, TRUE, NOW(), 'Claudia Munoz', 'CC', '1003003010', 'clmu@pulsia.com', 'Especialista', '3003000010', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'rica@pulsia.com', 'Ricardo', 'Castro', 'rica@pulsia.com', FALSE, TRUE, NOW(), 'Ricardo Castro', 'CC', '1003003011', 'rica@pulsia.com', 'Especialista', '3003000011', TRUE);

-- ESPECIALISTAS: Pediatria (ESP 10-12)
INSERT INTO agendamiento_customuser
  (password, last_login, is_superuser, username, first_name, last_name, email,
   is_staff, is_active, date_joined,
   nombre_completo, tipo_documento, num_documento, correo, rol, telefono, estado_cuenta)
VALUES
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'lube@pulsia.com', 'Lucia', 'Bermudez', 'lube@pulsia.com', FALSE, TRUE, NOW(), 'Lucia Bermudez', 'CC', '1003003012', 'lube@pulsia.com', 'Especialista', '3003000012', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'dago@pulsia.com', 'Daniel', 'Gomez', 'dago@pulsia.com', FALSE, TRUE, NOW(), 'Daniel Gomez', 'CC', '1003003013', 'dago@pulsia.com', 'Especialista', '3003000013', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'para@pulsia.com', 'Paula', 'Ramirez', 'para@pulsia.com', FALSE, TRUE, NOW(), 'Paula Ramirez', 'CC', '1003003014', 'para@pulsia.com', 'Especialista', '3003000014', TRUE);

-- ESPECIALISTAS: Ginecologia (ESP 13-15)
INSERT INTO agendamiento_customuser
  (password, last_login, is_superuser, username, first_name, last_name, email,
   is_staff, is_active, date_joined,
   nombre_completo, tipo_documento, num_documento, correo, rol, telefono, estado_cuenta)
VALUES
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'camo@pulsia.com', 'Camila', 'Morales', 'camo@pulsia.com', FALSE, TRUE, NOW(), 'Camila Morales', 'CC', '1003003015', 'camo@pulsia.com', 'Especialista', '3003000015', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'sori@pulsia.com', 'Sofia', 'Rios', 'sori@pulsia.com', FALSE, TRUE, NOW(), 'Sofia Rios', 'CC', '1003003016', 'sori@pulsia.com', 'Especialista', '3003000016', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'niol@pulsia.com', 'Nicolas', 'Olarte', 'niol@pulsia.com', FALSE, TRUE, NOW(), 'Nicolas Olarte', 'CC', '1003003017', 'niol@pulsia.com', 'Especialista', '3003000017', TRUE);

-- ESPECIALISTAS: Dermatologia (ESP 16-18)
INSERT INTO agendamiento_customuser
  (password, last_login, is_superuser, username, first_name, last_name, email,
   is_staff, is_active, date_joined,
   nombre_completo, tipo_documento, num_documento, correo, rol, telefono, estado_cuenta)
VALUES
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'ispe@pulsia.com', 'Isabel', 'Pena', 'ispe@pulsia.com', FALSE, TRUE, NOW(), 'Isabel Pena', 'CC', '1003003018', 'ispe@pulsia.com', 'Especialista', '3003000018', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'hera@pulsia.com', 'Hernan', 'Ramos', 'hera@pulsia.com', FALSE, TRUE, NOW(), 'Hernan Ramos', 'CC', '1003003019', 'hera@pulsia.com', 'Especialista', '3003000019', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'nivi@pulsia.com', 'Nives', 'Villa', 'nivi@pulsia.com', FALSE, TRUE, NOW(), 'Nives Villa', 'CC', '1003003020', 'nivi@pulsia.com', 'Especialista', '3003000020', TRUE);

-- ESPECIALISTAS: Psicologia (ESP 19-21)
INSERT INTO agendamiento_customuser
  (password, last_login, is_superuser, username, first_name, last_name, email,
   is_staff, is_active, date_joined,
   nombre_completo, tipo_documento, num_documento, correo, rol, telefono, estado_cuenta)
VALUES
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'alco@pulsia.com', 'Alejandro', 'Cordoba', 'alco@pulsia.com', FALSE, TRUE, NOW(), 'Alejandro Cordoba', 'CC', '1003003021', 'alco@pulsia.com', 'Especialista', '3003000021', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'gusa@pulsia.com', 'Gustavo', 'Salcedo', 'gusa@pulsia.com', FALSE, TRUE, NOW(), 'Gustavo Salcedo', 'CC', '1003003022', 'gusa@pulsia.com', 'Especialista', '3003000022', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'angu@pulsia.com', 'Angela', 'Guerrero', 'angu@pulsia.com', FALSE, TRUE, NOW(), 'Angela Guerrero', 'CC', '1003003023', 'angu@pulsia.com', 'Especialista', '3003000023', TRUE);

-- 100 PACIENTES
INSERT INTO agendamiento_customuser
  (password, last_login, is_superuser, username, first_name, last_name, email,
   is_staff, is_active, date_joined,
   nombre_completo, tipo_documento, num_documento, correo, rol, telefono, estado_cuenta)
VALUES
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'pema@pulsia.com', 'Pedro', 'Martinez', 'pema@pulsia.com', FALSE, TRUE, NOW(), 'Pedro Martinez', 'CC', '1004004004', 'pema@pulsia.com', 'Paciente', '3004000001', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'luna001@pulsia.com', 'Carlos', 'Luna', 'luna001@pulsia.com', FALSE, TRUE, NOW(), 'Carlos Luna', 'CC', '1004000002', 'luna001@pulsia.com', 'Paciente', '3004000002', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'meza002@pulsia.com', 'Maria', 'Meza', 'meza002@pulsia.com', FALSE, TRUE, NOW(), 'Maria Meza', 'CC', '1004000003', 'meza002@pulsia.com', 'Paciente', '3004000003', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'sosa003@pulsia.com', 'Juan', 'Sosa', 'sosa003@pulsia.com', FALSE, TRUE, NOW(), 'Juan Sosa', 'CC', '1004000004', 'sosa003@pulsia.com', 'Paciente', '3004000004', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'vega004@pulsia.com', 'Ana', 'Vega', 'vega004@pulsia.com', FALSE, TRUE, NOW(), 'Ana Vega', 'CC', '1004000005', 'vega004@pulsia.com', 'Paciente', '3004000005', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'rios005@pulsia.com', 'Laura', 'Rios', 'rios005@pulsia.com', FALSE, TRUE, NOW(), 'Laura Rios', 'CC', '1004000006', 'rios005@pulsia.com', 'Paciente', '3004000006', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'nino006@pulsia.com', 'Diego', 'Nino', 'nino006@pulsia.com', FALSE, TRUE, NOW(), 'Diego Nino', 'CC', '1004000007', 'nino006@pulsia.com', 'Paciente', '3004000007', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'ruiz007@pulsia.com', 'Paula', 'Ruiz', 'ruiz007@pulsia.com', FALSE, TRUE, NOW(), 'Paula Ruiz', 'CC', '1004000008', 'ruiz007@pulsia.com', 'Paciente', '3004000008', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'alba008@pulsia.com', 'Jorge', 'Alba', 'alba008@pulsia.com', FALSE, TRUE, NOW(), 'Jorge Alba', 'CC', '1004000009', 'alba008@pulsia.com', 'Paciente', '3004000009', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'mora009@pulsia.com', 'Lucia', 'Mora', 'mora009@pulsia.com', FALSE, TRUE, NOW(), 'Lucia Mora', 'CC', '1004000010', 'mora009@pulsia.com', 'Paciente', '3004000010', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'pino010@pulsia.com', 'Camila', 'Pino', 'pino010@pulsia.com', FALSE, TRUE, NOW(), 'Camila Pino', 'CC', '1004000011', 'pino010@pulsia.com', 'Paciente', '3004000011', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'cano011@pulsia.com', 'Miguel', 'Cano', 'cano011@pulsia.com', FALSE, TRUE, NOW(), 'Miguel Cano', 'CC', '1004000012', 'cano011@pulsia.com', 'Paciente', '3004000012', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'ovalle012@pulsia.com', 'Natalia', 'Ovalle', 'ovalle012@pulsia.com', FALSE, TRUE, NOW(), 'Natalia Ovalle', 'CC', '1004000013', 'ovalle012@pulsia.com', 'Paciente', '3004000013', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'cruz013@pulsia.com', 'Sebastian', 'Cruz', 'cruz013@pulsia.com', FALSE, TRUE, NOW(), 'Sebastian Cruz', 'CC', '1004000014', 'cruz013@pulsia.com', 'Paciente', '3004000014', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'leal014@pulsia.com', 'Valeria', 'Leal', 'leal014@pulsia.com', FALSE, TRUE, NOW(), 'Valeria Leal', 'CC', '1004000015', 'leal014@pulsia.com', 'Paciente', '3004000015', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'ferro015@pulsia.com', 'Felipe', 'Ferro', 'ferro015@pulsia.com', FALSE, TRUE, NOW(), 'Felipe Ferro', 'CC', '1004000016', 'ferro015@pulsia.com', 'Paciente', '3004000016', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'daza016@pulsia.com', 'Sara', 'Daza', 'daza016@pulsia.com', FALSE, TRUE, NOW(), 'Sara Daza', 'CC', '1004000017', 'daza016@pulsia.com', 'Paciente', '3004000017', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'perez017@pulsia.com', 'Manuel', 'Perez', 'perez017@pulsia.com', FALSE, TRUE, NOW(), 'Manuel Perez', 'CC', '1004000018', 'perez017@pulsia.com', 'Paciente', '3004000018', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'gil018@pulsia.com', 'Isabela', 'Gil', 'gil018@pulsia.com', FALSE, TRUE, NOW(), 'Isabela Gil', 'CC', '1004000019', 'gil018@pulsia.com', 'Paciente', '3004000019', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'lara019@pulsia.com', 'Tomas', 'Lara', 'lara019@pulsia.com', FALSE, TRUE, NOW(), 'Tomas Lara', 'CC', '1004000020', 'lara019@pulsia.com', 'Paciente', '3004000020', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'baez020@pulsia.com', 'Daniela', 'Baez', 'baez020@pulsia.com', FALSE, TRUE, NOW(), 'Daniela Baez', 'CC', '1004000021', 'baez020@pulsia.com', 'Paciente', '3004000021', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'reyes021@pulsia.com', 'Andres', 'Reyes', 'reyes021@pulsia.com', FALSE, TRUE, NOW(), 'Andres Reyes', 'CC', '1004000022', 'reyes021@pulsia.com', 'Paciente', '3004000022', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'olmos022@pulsia.com', 'Tatiana', 'Olmos', 'olmos022@pulsia.com', FALSE, TRUE, NOW(), 'Tatiana Olmos', 'CC', '1004000023', 'olmos022@pulsia.com', 'Paciente', '3004000023', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'patino023@pulsia.com', 'Oscar', 'Patino', 'patino023@pulsia.com', FALSE, TRUE, NOW(), 'Oscar Patino', 'CC', '1004000024', 'patino023@pulsia.com', 'Paciente', '3004000024', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'ossa024@pulsia.com', 'Gloria', 'Ossa', 'ossa024@pulsia.com', FALSE, TRUE, NOW(), 'Gloria Ossa', 'CC', '1004000025', 'ossa024@pulsia.com', 'Paciente', '3004000025', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'arias025@pulsia.com', 'David', 'Arias', 'arias025@pulsia.com', FALSE, TRUE, NOW(), 'David Arias', 'CC', '1004000026', 'arias025@pulsia.com', 'Paciente', '3004000026', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'rico026@pulsia.com', 'Erika', 'Rico', 'rico026@pulsia.com', FALSE, TRUE, NOW(), 'Erika Rico', 'CC', '1004000027', 'rico026@pulsia.com', 'Paciente', '3004000027', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'suarez027@pulsia.com', 'Bernardo', 'Suarez', 'suarez027@pulsia.com', FALSE, TRUE, NOW(), 'Bernardo Suarez', 'CC', '1004000028', 'suarez027@pulsia.com', 'Paciente', '3004000028', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'vera028@pulsia.com', 'Juana', 'Vera', 'vera028@pulsia.com', FALSE, TRUE, NOW(), 'Juana Vera', 'CC', '1004000029', 'vera028@pulsia.com', 'Paciente', '3004000029', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'nieto029@pulsia.com', 'Julian', 'Nieto', 'nieto029@pulsia.com', FALSE, TRUE, NOW(), 'Julian Nieto', 'CC', '1004000030', 'nieto029@pulsia.com', 'Paciente', '3004000030', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'serrano030@pulsia.com', 'Patricia', 'Serrano', 'serrano030@pulsia.com', FALSE, TRUE, NOW(), 'Patricia Serrano', 'CC', '1004000031', 'serrano030@pulsia.com', 'Paciente', '3004000031', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'parra031@pulsia.com', 'Rodrigo', 'Parra', 'parra031@pulsia.com', FALSE, TRUE, NOW(), 'Rodrigo Parra', 'CC', '1004000032', 'parra031@pulsia.com', 'Paciente', '3004000032', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'gomez032@pulsia.com', 'Marina', 'Gomez', 'gomez032@pulsia.com', FALSE, TRUE, NOW(), 'Marina Gomez', 'CC', '1004000033', 'gomez032@pulsia.com', 'Paciente', '3004000033', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'bolivar033@pulsia.com', 'Nelson', 'Bolivar', 'bolivar033@pulsia.com', FALSE, TRUE, NOW(), 'Nelson Bolivar', 'CC', '1004000034', 'bolivar033@pulsia.com', 'Paciente', '3004000034', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'vargas034@pulsia.com', 'Rebeca', 'Vargas', 'vargas034@pulsia.com', FALSE, TRUE, NOW(), 'Rebeca Vargas', 'CC', '1004000035', 'vargas034@pulsia.com', 'Paciente', '3004000035', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'casas035@pulsia.com', 'Fernando', 'Casas', 'casas035@pulsia.com', FALSE, TRUE, NOW(), 'Fernando Casas', 'CC', '1004000036', 'casas035@pulsia.com', 'Paciente', '3004000036', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'leon036@pulsia.com', 'Helena', 'Leon', 'leon036@pulsia.com', FALSE, TRUE, NOW(), 'Helena Leon', 'CC', '1004000037', 'leon036@pulsia.com', 'Paciente', '3004000037', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'molina037@pulsia.com', 'Walter', 'Molina', 'molina037@pulsia.com', FALSE, TRUE, NOW(), 'Walter Molina', 'CC', '1004000038', 'molina037@pulsia.com', 'Paciente', '3004000038', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'torres038@pulsia.com', 'Claudia', 'Torres', 'torres038@pulsia.com', FALSE, TRUE, NOW(), 'Claudia Torres', 'CC', '1004000039', 'torres038@pulsia.com', 'Paciente', '3004000039', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'agudelo039@pulsia.com', 'German', 'Agudelo', 'agudelo039@pulsia.com', FALSE, TRUE, NOW(), 'German Agudelo', 'CC', '1004000040', 'agudelo039@pulsia.com', 'Paciente', '3004000040', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'duarte040@pulsia.com', 'Carolina', 'Duarte', 'duarte040@pulsia.com', FALSE, TRUE, NOW(), 'Carolina Duarte', 'CC', '1004000041', 'duarte040@pulsia.com', 'Paciente', '3004000041', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'ospina041@pulsia.com', 'Harold', 'Ospina', 'ospina041@pulsia.com', FALSE, TRUE, NOW(), 'Harold Ospina', 'CC', '1004000042', 'ospina041@pulsia.com', 'Paciente', '3004000042', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'florez042@pulsia.com', 'Monica', 'Florez', 'florez042@pulsia.com', FALSE, TRUE, NOW(), 'Monica Florez', 'CC', '1004000043', 'florez042@pulsia.com', 'Paciente', '3004000043', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'bautista043@pulsia.com', 'Ivan', 'Bautista', 'bautista043@pulsia.com', FALSE, TRUE, NOW(), 'Ivan Bautista', 'CC', '1004000044', 'bautista043@pulsia.com', 'Paciente', '3004000044', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'mesa044@pulsia.com', 'Gloria', 'Mesa', 'mesa044@pulsia.com', FALSE, TRUE, NOW(), 'Gloria Mesa', 'CC', '1004000045', 'mesa044@pulsia.com', 'Paciente', '3004000045', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'henao045@pulsia.com', 'Cristian', 'Henao', 'henao045@pulsia.com', FALSE, TRUE, NOW(), 'Cristian Henao', 'CC', '1004000046', 'henao045@pulsia.com', 'Paciente', '3004000046', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'fajardo046@pulsia.com', 'Beatriz', 'Fajardo', 'fajardo046@pulsia.com', FALSE, TRUE, NOW(), 'Beatriz Fajardo', 'CC', '1004000047', 'fajardo046@pulsia.com', 'Paciente', '3004000047', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'mendez047@pulsia.com', 'Edwin', 'Mendez', 'mendez047@pulsia.com', FALSE, TRUE, NOW(), 'Edwin Mendez', 'CC', '1004000048', 'mendez047@pulsia.com', 'Paciente', '3004000048', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'navas048@pulsia.com', 'Sonia', 'Navas', 'navas048@pulsia.com', FALSE, TRUE, NOW(), 'Sonia Navas', 'CC', '1004000049', 'navas048@pulsia.com', 'Paciente', '3004000049', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'guerrero049@pulsia.com', 'Rafael', 'Guerrero', 'guerrero049@pulsia.com', FALSE, TRUE, NOW(), 'Rafael Guerrero', 'CC', '1004000050', 'guerrero049@pulsia.com', 'Paciente', '3004000050', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'salazar050@pulsia.com', 'Viviana', 'Salazar', 'salazar050@pulsia.com', FALSE, TRUE, NOW(), 'Viviana Salazar', 'CC', '1004000051', 'salazar050@pulsia.com', 'Paciente', '3004000051', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'arteaga051@pulsia.com', 'Jaime', 'Arteaga', 'arteaga051@pulsia.com', FALSE, TRUE, NOW(), 'Jaime Arteaga', 'CC', '1004000052', 'arteaga051@pulsia.com', 'Paciente', '3004000052', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'benitez052@pulsia.com', 'Diana', 'Benitez', 'benitez052@pulsia.com', FALSE, TRUE, NOW(), 'Diana Benitez', 'CC', '1004000053', 'benitez052@pulsia.com', 'Paciente', '3004000053', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'paredes053@pulsia.com', 'Humberto', 'Paredes', 'paredes053@pulsia.com', FALSE, TRUE, NOW(), 'Humberto Paredes', 'CC', '1004000054', 'paredes053@pulsia.com', 'Paciente', '3004000054', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'rincon054@pulsia.com', 'Paola', 'Rincon', 'rincon054@pulsia.com', FALSE, TRUE, NOW(), 'Paola Rincon', 'CC', '1004000055', 'rincon054@pulsia.com', 'Paciente', '3004000055', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'correa055@pulsia.com', 'Alirio', 'Correa', 'correa055@pulsia.com', FALSE, TRUE, NOW(), 'Alirio Correa', 'CC', '1004000056', 'correa055@pulsia.com', 'Paciente', '3004000056', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'ibarra056@pulsia.com', 'Sandra', 'Ibarra', 'ibarra056@pulsia.com', FALSE, TRUE, NOW(), 'Sandra Ibarra', 'CC', '1004000057', 'ibarra056@pulsia.com', 'Paciente', '3004000057', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'fuentes057@pulsia.com', 'Leandro', 'Fuentes', 'fuentes057@pulsia.com', FALSE, TRUE, NOW(), 'Leandro Fuentes', 'CC', '1004000058', 'fuentes057@pulsia.com', 'Paciente', '3004000058', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'montoya058@pulsia.com', 'Melisa', 'Montoya', 'montoya058@pulsia.com', FALSE, TRUE, NOW(), 'Melisa Montoya', 'CC', '1004000059', 'montoya058@pulsia.com', 'Paciente', '3004000059', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'cabra059@pulsia.com', 'Jhon', 'Cabra', 'cabra059@pulsia.com', FALSE, TRUE, NOW(), 'Jhon Cabra', 'CC', '1004000060', 'cabra059@pulsia.com', 'Paciente', '3004000060', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'solano060@pulsia.com', 'Lina', 'Solano', 'solano060@pulsia.com', FALSE, TRUE, NOW(), 'Lina Solano', 'CC', '1004000061', 'solano060@pulsia.com', 'Paciente', '3004000061', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'zapata061@pulsia.com', 'Omar', 'Zapata', 'zapata061@pulsia.com', FALSE, TRUE, NOW(), 'Omar Zapata', 'CC', '1004000062', 'zapata061@pulsia.com', 'Paciente', '3004000062', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'acosta062@pulsia.com', 'Angela', 'Acosta', 'acosta062@pulsia.com', FALSE, TRUE, NOW(), 'Angela Acosta', 'CC', '1004000063', 'acosta062@pulsia.com', 'Paciente', '3004000063', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'rocha063@pulsia.com', 'Ernesto', 'Rocha', 'rocha063@pulsia.com', FALSE, TRUE, NOW(), 'Ernesto Rocha', 'CC', '1004000064', 'rocha063@pulsia.com', 'Paciente', '3004000064', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'duran064@pulsia.com', 'Amanda', 'Duran', 'duran064@pulsia.com', FALSE, TRUE, NOW(), 'Amanda Duran', 'CC', '1004000065', 'duran064@pulsia.com', 'Paciente', '3004000065', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'escobar065@pulsia.com', 'Elkin', 'Escobar', 'escobar065@pulsia.com', FALSE, TRUE, NOW(), 'Elkin Escobar', 'CC', '1004000066', 'escobar065@pulsia.com', 'Paciente', '3004000066', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'palacio066@pulsia.com', 'Marcela', 'Palacio', 'palacio066@pulsia.com', FALSE, TRUE, NOW(), 'Marcela Palacio', 'CC', '1004000067', 'palacio066@pulsia.com', 'Paciente', '3004000067', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'betancur067@pulsia.com', 'Wilson', 'Betancur', 'betancur067@pulsia.com', FALSE, TRUE, NOW(), 'Wilson Betancur', 'CC', '1004000068', 'betancur067@pulsia.com', 'Paciente', '3004000068', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'angel068@pulsia.com', 'Yolanda', 'Angel', 'angel068@pulsia.com', FALSE, TRUE, NOW(), 'Yolanda Angel', 'CC', '1004000069', 'angel068@pulsia.com', 'Paciente', '3004000069', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'casta069@pulsia.com', 'Efrain', 'Castano', 'casta069@pulsia.com', FALSE, TRUE, NOW(), 'Efrain Castano', 'CC', '1004000070', 'casta069@pulsia.com', 'Paciente', '3004000070', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'guzman070@pulsia.com', 'Irene', 'Guzman', 'guzman070@pulsia.com', FALSE, TRUE, NOW(), 'Irene Guzman', 'CC', '1004000071', 'guzman070@pulsia.com', 'Paciente', '3004000071', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'rojas071@pulsia.com', 'Saul', 'Rojas', 'rojas071@pulsia.com', FALSE, TRUE, NOW(), 'Saul Rojas', 'CC', '1004000072', 'rojas071@pulsia.com', 'Paciente', '3004000072', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'duque072@pulsia.com', 'Constanza', 'Duque', 'duque072@pulsia.com', FALSE, TRUE, NOW(), 'Constanza Duque', 'CC', '1004000073', 'duque072@pulsia.com', 'Paciente', '3004000073', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'caro073@pulsia.com', 'Hernando', 'Caro', 'caro073@pulsia.com', FALSE, TRUE, NOW(), 'Hernando Caro', 'CC', '1004000074', 'caro073@pulsia.com', 'Paciente', '3004000074', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'sanchez074@pulsia.com', 'Luz', 'Sanchez', 'sanchez074@pulsia.com', FALSE, TRUE, NOW(), 'Luz Sanchez', 'CC', '1004000075', 'sanchez074@pulsia.com', 'Paciente', '3004000075', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'camacho075@pulsia.com', 'Mario', 'Camacho', 'camacho075@pulsia.com', FALSE, TRUE, NOW(), 'Mario Camacho', 'CC', '1004000076', 'camacho075@pulsia.com', 'Paciente', '3004000076', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'leon076@pulsia.com', 'Rocio', 'Leon', 'leon076@pulsia.com', FALSE, TRUE, NOW(), 'Rocio Leon', 'CC', '1004000077', 'leon076@pulsia.com', 'Paciente', '3004000077', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'neira077@pulsia.com', 'Alvaro', 'Neira', 'neira077@pulsia.com', FALSE, TRUE, NOW(), 'Alvaro Neira', 'CC', '1004000078', 'neira077@pulsia.com', 'Paciente', '3004000078', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'triana078@pulsia.com', 'Yenny', 'Triana', 'triana078@pulsia.com', FALSE, TRUE, NOW(), 'Yenny Triana', 'CC', '1004000079', 'triana078@pulsia.com', 'Paciente', '3004000079', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'galvis079@pulsia.com', 'Jose', 'Galvis', 'galvis079@pulsia.com', FALSE, TRUE, NOW(), 'Jose Galvis', 'CC', '1004000080', 'galvis079@pulsia.com', 'Paciente', '3004000080', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'saenz080@pulsia.com', 'Adriana', 'Saenz', 'saenz080@pulsia.com', FALSE, TRUE, NOW(), 'Adriana Saenz', 'CC', '1004000081', 'saenz080@pulsia.com', 'Paciente', '3004000081', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'celis081@pulsia.com', 'Jonathan', 'Celis', 'celis081@pulsia.com', FALSE, TRUE, NOW(), 'Jonathan Celis', 'CC', '1004000082', 'celis081@pulsia.com', 'Paciente', '3004000082', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'sandoval082@pulsia.com', 'Norma', 'Sandoval', 'sandoval082@pulsia.com', FALSE, TRUE, NOW(), 'Norma Sandoval', 'CC', '1004000083', 'sandoval082@pulsia.com', 'Paciente', '3004000083', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'pineda083@pulsia.com', 'Dario', 'Pineda', 'pineda083@pulsia.com', FALSE, TRUE, NOW(), 'Dario Pineda', 'CC', '1004000084', 'pineda083@pulsia.com', 'Paciente', '3004000084', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'camargo084@pulsia.com', 'Andrea', 'Camargo', 'camargo084@pulsia.com', FALSE, TRUE, NOW(), 'Andrea Camargo', 'CC', '1004000085', 'camargo084@pulsia.com', 'Paciente', '3004000085', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'orozco085@pulsia.com', 'Genaro', 'Orozco', 'orozco085@pulsia.com', FALSE, TRUE, NOW(), 'Genaro Orozco', 'CC', '1004000086', 'orozco085@pulsia.com', 'Paciente', '3004000086', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'villamizar086@pulsia.com', 'Elena', 'Villamizar', 'villamizar086@pulsia.com', FALSE, TRUE, NOW(), 'Elena Villamizar', 'CC', '1004000087', 'villamizar086@pulsia.com', 'Paciente', '3004000087', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'barrero087@pulsia.com', 'Fabio', 'Barrero', 'barrero087@pulsia.com', FALSE, TRUE, NOW(), 'Fabio Barrero', 'CC', '1004000088', 'barrero087@pulsia.com', 'Paciente', '3004000088', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'herrera088@pulsia.com', 'Stella', 'Herrera', 'herrera088@pulsia.com', FALSE, TRUE, NOW(), 'Stella Herrera', 'CC', '1004000089', 'herrera088@pulsia.com', 'Paciente', '3004000089', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'silva089@pulsia.com', 'Rodrigo', 'Silva', 'silva089@pulsia.com', FALSE, TRUE, NOW(), 'Rodrigo Silva', 'CC', '1004000090', 'silva089@pulsia.com', 'Paciente', '3004000090', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'rubio090@pulsia.com', 'Patricia', 'Rubio', 'rubio090@pulsia.com', FALSE, TRUE, NOW(), 'Patricia Rubio', 'CC', '1004000091', 'rubio090@pulsia.com', 'Paciente', '3004000091', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'mateus091@pulsia.com', 'Leonardo', 'Mateus', 'mateus091@pulsia.com', FALSE, TRUE, NOW(), 'Leonardo Mateus', 'CC', '1004000092', 'mateus091@pulsia.com', 'Paciente', '3004000092', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'velasco092@pulsia.com', 'Rosa', 'Velasco', 'velasco092@pulsia.com', FALSE, TRUE, NOW(), 'Rosa Velasco', 'CC', '1004000093', 'velasco092@pulsia.com', 'Paciente', '3004000093', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'posada093@pulsia.com', 'Ramiro', 'Posada', 'posada093@pulsia.com', FALSE, TRUE, NOW(), 'Ramiro Posada', 'CC', '1004000094', 'posada093@pulsia.com', 'Paciente', '3004000094', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'pinto094@pulsia.com', 'Flor', 'Pinto', 'pinto094@pulsia.com', FALSE, TRUE, NOW(), 'Flor Pinto', 'CC', '1004000095', 'pinto094@pulsia.com', 'Paciente', '3004000095', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'contreras095@pulsia.com', 'Yesid', 'Contreras', 'contreras095@pulsia.com', FALSE, TRUE, NOW(), 'Yesid Contreras', 'CC', '1004000096', 'contreras095@pulsia.com', 'Paciente', '3004000096', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'ceron096@pulsia.com', 'Helena', 'Ceron', 'ceron096@pulsia.com', FALSE, TRUE, NOW(), 'Helena Ceron', 'CC', '1004000097', 'ceron096@pulsia.com', 'Paciente', '3004000097', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'roa097@pulsia.com', 'Ernesto', 'Roa', 'roa097@pulsia.com', FALSE, TRUE, NOW(), 'Ernesto Roa', 'CC', '1004000098', 'roa097@pulsia.com', 'Paciente', '3004000098', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'puentes098@pulsia.com', 'Zoila', 'Puentes', 'puentes098@pulsia.com', FALSE, TRUE, NOW(), 'Zoila Puentes', 'CC', '1004000099', 'puentes098@pulsia.com', 'Paciente', '3004000099', TRUE),
  ('pbkdf2_sha256$1200000$SuFw0mU6iAOhytNK5mMyKx$i4vi83IIIXLWuKSdTIWUC6k2EpWRkhaXsiMfQNICHOM=', NULL, FALSE, 'tovar099@pulsia.com', 'Alexander', 'Tovar', 'tovar099@pulsia.com', FALSE, TRUE, NOW(), 'Alexander Tovar', 'CC', '1004000100', 'tovar099@pulsia.com', 'Paciente', '3004000100', TRUE);

-- =============================================================================
-- PASO 4: ESPECIALIDADES
-- =============================================================================
INSERT INTO agendamiento_especialidad (nombre_especialidad, descripcion) VALUES
  ('Medicina General',  'Atencion medica primaria y diagnostico inicial.'),
  ('Odontologia',       'Salud bucodental, prevencion y tratamiento dental.'),
  ('Cardiologia',       'Diagnostico y tratamiento de enfermedades del corazon.'),
  ('Pediatria',         'Atencion integral para ninos y adolescentes.'),
  ('Ginecologia',       'Salud femenina, ginecologia y obstetricia.'),
  ('Dermatologia',      'Diagnostico y tratamiento de enfermedades de la piel.'),
  ('Psicologia',        'Acompanamiento emocional, salud mental y terapia.');

-- =============================================================================
-- PASO 5: CONSULTORIOS (21 — uno por especialista)
-- =============================================================================
INSERT INTO agendamiento_consultorio (nombre_codigo, estado_operativo) VALUES
  ('MG-101', TRUE), ('MG-102', TRUE), ('MG-103', TRUE),
  ('OD-201', TRUE), ('OD-202', TRUE), ('OD-203', TRUE),
  ('CA-301', TRUE), ('CA-302', TRUE), ('CA-303', TRUE),
  ('PE-401', TRUE), ('PE-402', TRUE), ('PE-403', TRUE),
  ('GI-501', TRUE), ('GI-502', TRUE), ('GI-503', TRUE),
  ('DE-601', TRUE), ('DE-602', TRUE), ('DE-603', TRUE),
  ('PS-701', TRUE), ('PS-702', TRUE), ('PS-703', TRUE);

-- =============================================================================
-- PASO 6: PERFILES PACIENTE (genera los 100 automaticamente)
-- =============================================================================
INSERT INTO agendamiento_paciente (usuario_id, fecha_nacimiento, acepta_habeas_data, contador_inasistencias)
SELECT
  u.id,
  ('1960-01-01'::date + (((ROW_NUMBER() OVER (ORDER BY u.id) - 1) * 137) % (365 * 50)) * INTERVAL '1 day')::date,
  TRUE,
  0
FROM agendamiento_customuser u
WHERE u.rol = 'Paciente'
ORDER BY u.id;

-- =============================================================================
-- PASO 7: PERFILES ESPECIALISTA + CONSULTORIO
-- =============================================================================
INSERT INTO agendamiento_especialista (usuario_id, especialidad_id, consultorio_id, estado_turno)
SELECT u.id, espid, consid, 'Ausente'
FROM agendamiento_customuser u
JOIN (VALUES
  ('cape@pulsia.com', 1, 1),  ('maro@pulsia.com', 1, 2),  ('jime@pulsia.com', 1, 3),
  ('sato@pulsia.com', 2, 4),  ('feva@pulsia.com', 2, 5),  ('vale@pulsia.com', 2, 6),
  ('anso@pulsia.com', 3, 7),  ('clmu@pulsia.com', 3, 8),  ('rica@pulsia.com', 3, 9),
  ('lube@pulsia.com', 4, 10), ('dago@pulsia.com', 4, 11), ('para@pulsia.com', 4, 12),
  ('camo@pulsia.com', 5, 13), ('sori@pulsia.com', 5, 14), ('niol@pulsia.com', 5, 15),
  ('ispe@pulsia.com', 6, 16), ('hera@pulsia.com', 6, 17), ('nivi@pulsia.com', 6, 18),
  ('alco@pulsia.com', 7, 19), ('gusa@pulsia.com', 7, 20), ('angu@pulsia.com', 7, 21)
) AS m(correo, espid, consid) ON u.correo = m.correo;

-- =============================================================================
-- PASO 8: HORARIOS LABORALES
-- Patron: ESP1=Manana, ESP2=Tarde, ESP3=Completo (varia por especialidad)
-- dias: 1=Lun, 2=Mar, 3=Mie, 4=Jue, 5=Vie, 6=Sab
-- =============================================================================
INSERT INTO agendamiento_horariolaboral
  (especialista_id, dia_semana, hora_inicio, hora_fin, hora_inicio_descanso, hora_fin_descanso)
SELECT e.id, hl.dia, hl.ini::time, hl.fin::time, hl.di::time, hl.df::time
FROM agendamiento_especialista e
JOIN agendamiento_customuser u ON e.usuario_id = u.id
JOIN (VALUES
  -- Medicina General ESP1 (cape) - MANANA Lun-Vie
  ('cape@pulsia.com',1,'08:00','13:00',NULL,NULL),
  ('cape@pulsia.com',2,'08:00','13:00',NULL,NULL),
  ('cape@pulsia.com',3,'08:00','13:00',NULL,NULL),
  ('cape@pulsia.com',4,'08:00','13:00',NULL,NULL),
  ('cape@pulsia.com',5,'08:00','13:00',NULL,NULL),
  -- Medicina General ESP2 (maro) - TARDE Lun-Vie
  ('maro@pulsia.com',1,'14:00','17:30',NULL,NULL),
  ('maro@pulsia.com',2,'14:00','17:30',NULL,NULL),
  ('maro@pulsia.com',3,'14:00','17:30',NULL,NULL),
  ('maro@pulsia.com',4,'14:00','17:30',NULL,NULL),
  ('maro@pulsia.com',5,'14:00','17:30',NULL,NULL),
  -- Medicina General ESP3 (jime) - COMPLETO Lun-Sab
  ('jime@pulsia.com',1,'08:00','17:30','12:00','14:00'),
  ('jime@pulsia.com',2,'08:00','17:30','12:00','14:00'),
  ('jime@pulsia.com',3,'08:00','17:30','12:00','14:00'),
  ('jime@pulsia.com',4,'08:00','17:30','12:00','14:00'),
  ('jime@pulsia.com',5,'08:00','17:30','12:00','14:00'),
  ('jime@pulsia.com',6,'08:00','12:00',NULL,NULL),
  -- Odontologia ESP1 (sato) - MANANA Lun-Jue+Sab
  ('sato@pulsia.com',1,'08:00','13:00',NULL,NULL),
  ('sato@pulsia.com',2,'08:00','13:00',NULL,NULL),
  ('sato@pulsia.com',3,'08:00','13:00',NULL,NULL),
  ('sato@pulsia.com',4,'08:00','13:00',NULL,NULL),
  ('sato@pulsia.com',6,'08:00','13:00',NULL,NULL),
  -- Odontologia ESP2 (feva) - TARDE Mar-Vie
  ('feva@pulsia.com',2,'14:00','18:00',NULL,NULL),
  ('feva@pulsia.com',3,'14:00','18:00',NULL,NULL),
  ('feva@pulsia.com',4,'14:00','18:00',NULL,NULL),
  ('feva@pulsia.com',5,'14:00','18:00',NULL,NULL),
  -- Odontologia ESP3 (vale) - COMPLETO Lun-Vie
  ('vale@pulsia.com',1,'07:30','17:00','12:00','13:00'),
  ('vale@pulsia.com',2,'07:30','17:00','12:00','13:00'),
  ('vale@pulsia.com',3,'07:30','17:00','12:00','13:00'),
  ('vale@pulsia.com',4,'07:30','17:00','12:00','13:00'),
  ('vale@pulsia.com',5,'07:30','17:00','12:00','13:00'),
  -- Cardiologia ESP1 (anso) - MANANA Lun-Mie
  ('anso@pulsia.com',1,'08:00','13:00',NULL,NULL),
  ('anso@pulsia.com',2,'08:00','13:00',NULL,NULL),
  ('anso@pulsia.com',3,'08:00','13:00',NULL,NULL),
  -- Cardiologia ESP2 (clmu) - TARDE Jue-Vie+Sab
  ('clmu@pulsia.com',4,'14:00','18:00',NULL,NULL),
  ('clmu@pulsia.com',5,'14:00','18:00',NULL,NULL),
  ('clmu@pulsia.com',6,'08:00','13:00',NULL,NULL),
  -- Cardiologia ESP3 (rica) - COMPLETO Lun-Vie
  ('rica@pulsia.com',1,'07:00','17:00','12:30','13:30'),
  ('rica@pulsia.com',2,'07:00','17:00','12:30','13:30'),
  ('rica@pulsia.com',3,'07:00','17:00','12:30','13:30'),
  ('rica@pulsia.com',4,'07:00','17:00','12:30','13:30'),
  ('rica@pulsia.com',5,'07:00','17:00','12:30','13:30'),
  -- Pediatria ESP1 (lube) - MANANA Lun-Vie
  ('lube@pulsia.com',1,'08:00','12:30',NULL,NULL),
  ('lube@pulsia.com',2,'08:00','12:30',NULL,NULL),
  ('lube@pulsia.com',3,'08:00','12:30',NULL,NULL),
  ('lube@pulsia.com',4,'08:00','12:30',NULL,NULL),
  ('lube@pulsia.com',5,'08:00','12:30',NULL,NULL),
  -- Pediatria ESP2 (dago) - TARDE Lun-Jue
  ('dago@pulsia.com',1,'13:30','18:00',NULL,NULL),
  ('dago@pulsia.com',2,'13:30','18:00',NULL,NULL),
  ('dago@pulsia.com',3,'13:30','18:00',NULL,NULL),
  ('dago@pulsia.com',4,'13:30','18:00',NULL,NULL),
  -- Pediatria ESP3 (para) - COMPLETO Lun-Sab
  ('para@pulsia.com',1,'08:00','18:00','12:00','14:00'),
  ('para@pulsia.com',2,'08:00','18:00','12:00','14:00'),
  ('para@pulsia.com',3,'08:00','18:00','12:00','14:00'),
  ('para@pulsia.com',4,'08:00','18:00','12:00','14:00'),
  ('para@pulsia.com',5,'08:00','18:00','12:00','14:00'),
  ('para@pulsia.com',6,'09:00','13:00',NULL,NULL),
  -- Ginecologia ESP1 (camo) - MANANA Lun-Vie
  ('camo@pulsia.com',1,'08:00','13:00',NULL,NULL),
  ('camo@pulsia.com',2,'08:00','13:00',NULL,NULL),
  ('camo@pulsia.com',3,'08:00','13:00',NULL,NULL),
  ('camo@pulsia.com',4,'08:00','13:00',NULL,NULL),
  ('camo@pulsia.com',5,'08:00','13:00',NULL,NULL),
  -- Ginecologia ESP2 (sori) - TARDE Mar-Sab
  ('sori@pulsia.com',2,'14:00','18:00',NULL,NULL),
  ('sori@pulsia.com',3,'14:00','18:00',NULL,NULL),
  ('sori@pulsia.com',4,'14:00','18:00',NULL,NULL),
  ('sori@pulsia.com',5,'14:00','18:00',NULL,NULL),
  ('sori@pulsia.com',6,'08:00','13:00',NULL,NULL),
  -- Ginecologia ESP3 (niol) - COMPLETO Mie-Vie
  ('niol@pulsia.com',3,'07:00','18:00','12:00','14:00'),
  ('niol@pulsia.com',4,'07:00','18:00','12:00','14:00'),
  ('niol@pulsia.com',5,'07:00','18:00','12:00','14:00'),
  -- Dermatologia ESP1 (ispe) - MANANA Lun-Jue
  ('ispe@pulsia.com',1,'08:00','13:00',NULL,NULL),
  ('ispe@pulsia.com',2,'08:00','13:00',NULL,NULL),
  ('ispe@pulsia.com',3,'08:00','13:00',NULL,NULL),
  ('ispe@pulsia.com',4,'08:00','13:00',NULL,NULL),
  -- Dermatologia ESP2 (hera) - TARDE Lun-Vie
  ('hera@pulsia.com',1,'14:00','18:00',NULL,NULL),
  ('hera@pulsia.com',2,'14:00','18:00',NULL,NULL),
  ('hera@pulsia.com',3,'14:00','18:00',NULL,NULL),
  ('hera@pulsia.com',4,'14:00','18:00',NULL,NULL),
  ('hera@pulsia.com',5,'14:00','18:00',NULL,NULL),
  -- Dermatologia ESP3 (nivi) - COMPLETO Lun-Sab
  ('nivi@pulsia.com',1,'08:00','17:30','12:30','13:30'),
  ('nivi@pulsia.com',2,'08:00','17:30','12:30','13:30'),
  ('nivi@pulsia.com',3,'08:00','17:30','12:30','13:30'),
  ('nivi@pulsia.com',4,'08:00','17:30','12:30','13:30'),
  ('nivi@pulsia.com',5,'08:00','17:30','12:30','13:30'),
  ('nivi@pulsia.com',6,'08:00','12:00',NULL,NULL),
  -- Psicologia ESP1 (alco) - MANANA Lun-Vie
  ('alco@pulsia.com',1,'08:00','13:00',NULL,NULL),
  ('alco@pulsia.com',2,'08:00','13:00',NULL,NULL),
  ('alco@pulsia.com',3,'08:00','13:00',NULL,NULL),
  ('alco@pulsia.com',4,'08:00','13:00',NULL,NULL),
  ('alco@pulsia.com',5,'08:00','13:00',NULL,NULL),
  -- Psicologia ESP2 (gusa) - TARDE Lun-Jue+Sab
  ('gusa@pulsia.com',1,'14:00','18:00',NULL,NULL),
  ('gusa@pulsia.com',2,'14:00','18:00',NULL,NULL),
  ('gusa@pulsia.com',3,'14:00','18:00',NULL,NULL),
  ('gusa@pulsia.com',4,'14:00','18:00',NULL,NULL),
  ('gusa@pulsia.com',6,'08:00','12:00',NULL,NULL),
  -- Psicologia ESP3 (angu) - COMPLETO Mar-Vie
  ('angu@pulsia.com',2,'07:30','17:30','12:00','13:00'),
  ('angu@pulsia.com',3,'07:30','17:30','12:00','13:00'),
  ('angu@pulsia.com',4,'07:30','17:30','12:00','13:00'),
  ('angu@pulsia.com',5,'07:30','17:30','12:00','13:00')
) AS hl(correo, dia, ini, fin, di, df) ON u.correo = hl.correo;

-- =============================================================================
-- PASO 9: CITAS AGOSTO 2026
-- Respeta horarios laborales de cada especialista
-- Sin cruces de agenda en el mismo especialista/hora
-- Festivo 7 ago (Batalla de Boyaca) excluido
-- =============================================================================
INSERT INTO agendamiento_cita
  (paciente_id, especialista_id, consultorio_id, fecha_hora_inicio, fecha_hora_fin,
   estado_cita, contador_reprogramacion, notas_clinicas)
SELECT
  p.id, e.id, e.consultorio_id,
  c.fi::timestamp, c.fi::timestamp + INTERVAL '30 minutes',
  c.est, 0, c.nota
FROM (VALUES
  -- MEDICINA GENERAL - Carlos Parra (cape) Manana 08:00-13:00 Lun-Vie
  ('cape@pulsia.com','pema@pulsia.com',         '2026-08-04 08:00','Atendida',    'Control anual completado.'),
  ('cape@pulsia.com','luna001@pulsia.com',       '2026-08-04 08:30','Atendida',    'Gripa estacional, se receto paracetamol.'),
  ('cape@pulsia.com','meza002@pulsia.com',       '2026-08-05 09:00','Atendida',    'Chequeo general sin novedad.'),
  ('cape@pulsia.com','sosa003@pulsia.com',       '2026-08-05 09:30','No_Asistio',  NULL),
  ('cape@pulsia.com','vega004@pulsia.com',       '2026-08-06 10:00','Atendida',    'Revision de presion arterial.'),
  ('cape@pulsia.com','rios005@pulsia.com',       '2026-08-11 08:00','Cancelada',   'Paciente cancelo con antelacion.'),
  ('cape@pulsia.com','nino006@pulsia.com',       '2026-08-11 08:30','Atendida',    'Infeccion respiratoria leve.'),
  ('cape@pulsia.com','ruiz007@pulsia.com',       '2026-08-12 08:00','Programada',  NULL),
  ('cape@pulsia.com','alba008@pulsia.com',       '2026-08-13 09:00','Programada',  NULL),
  ('cape@pulsia.com','mora009@pulsia.com',       '2026-08-14 10:00','Programada',  NULL),
  ('cape@pulsia.com','pino010@pulsia.com',       '2026-08-18 08:00','Programada',  NULL),
  ('cape@pulsia.com','cano011@pulsia.com',       '2026-08-19 08:30','Programada',  NULL),
  ('cape@pulsia.com','ovalle012@pulsia.com',     '2026-08-20 09:00','Programada',  NULL),
  ('cape@pulsia.com','cruz013@pulsia.com',       '2026-08-25 08:00','Programada',  NULL),
  ('cape@pulsia.com','leal014@pulsia.com',       '2026-08-26 09:30','Programada',  NULL),
  -- MEDICINA GENERAL - Maria Rodriguez (maro) Tarde 14:00-17:30 Lun-Vie
  ('maro@pulsia.com','ferro015@pulsia.com',      '2026-08-03 14:00','Atendida',    'Control de diabetes tipo 2.'),
  ('maro@pulsia.com','daza016@pulsia.com',       '2026-08-04 14:30','Atendida',    'Chequeo post-cirugia.'),
  ('maro@pulsia.com','perez017@pulsia.com',      '2026-08-05 15:00','No_Asistio',  NULL),
  ('maro@pulsia.com','gil018@pulsia.com',        '2026-08-06 14:00','Atendida',    'Consulta por cefalea recurrente.'),
  ('maro@pulsia.com','lara019@pulsia.com',       '2026-08-11 14:30','Programada',  NULL),
  ('maro@pulsia.com','baez020@pulsia.com',       '2026-08-12 15:00','Programada',  NULL),
  ('maro@pulsia.com','reyes021@pulsia.com',      '2026-08-13 14:00','Programada',  NULL),
  ('maro@pulsia.com','olmos022@pulsia.com',      '2026-08-18 14:30','Programada',  NULL),
  ('maro@pulsia.com','patino023@pulsia.com',     '2026-08-19 15:00','Programada',  NULL),
  ('maro@pulsia.com','ossa024@pulsia.com',       '2026-08-20 14:00','Programada',  NULL),
  ('maro@pulsia.com','arias025@pulsia.com',      '2026-08-25 14:30','Programada',  NULL),
  ('maro@pulsia.com','rico026@pulsia.com',       '2026-08-26 15:00','Programada',  NULL),
  -- MEDICINA GENERAL - Jimmy Mejia (jime) Completo Lun-Sab
  ('jime@pulsia.com','suarez027@pulsia.com',     '2026-08-03 08:00','Atendida',    'Dx: anemia ferropenica, se receto hierro.'),
  ('jime@pulsia.com','vera028@pulsia.com',       '2026-08-03 14:30','Atendida',    'Chequeo general adulto mayor.'),
  ('jime@pulsia.com','nieto029@pulsia.com',      '2026-08-04 09:00','Atendida',    'Dolor lumbar. Ordenada fisioterapia.'),
  ('jime@pulsia.com','serrano030@pulsia.com',    '2026-08-05 10:00','Cancelada',   NULL),
  ('jime@pulsia.com','parra031@pulsia.com',      '2026-08-08 08:30','Atendida',    'Revision de resultados de laboratorio.'),
  ('jime@pulsia.com','gomez032@pulsia.com',      '2026-08-10 09:00','Atendida',    'Gripa con complicacion leve.'),
  ('jime@pulsia.com','bolivar033@pulsia.com',    '2026-08-11 08:00','En_Sala',     NULL),
  ('jime@pulsia.com','vargas034@pulsia.com',     '2026-08-12 14:00','Programada',  NULL),
  ('jime@pulsia.com','casas035@pulsia.com',      '2026-08-13 09:30','Programada',  NULL),
  ('jime@pulsia.com','leon036@pulsia.com',       '2026-08-15 08:00','Programada',  NULL),
  ('jime@pulsia.com','molina037@pulsia.com',     '2026-08-17 08:00','Programada',  NULL),
  ('jime@pulsia.com','torres038@pulsia.com',     '2026-08-18 09:00','Programada',  NULL),
  ('jime@pulsia.com','agudelo039@pulsia.com',    '2026-08-19 14:30','Programada',  NULL),
  ('jime@pulsia.com','duarte040@pulsia.com',     '2026-08-20 08:30','Programada',  NULL),
  ('jime@pulsia.com','ospina041@pulsia.com',     '2026-08-22 08:00','Programada',  NULL),
  -- ODONTOLOGIA - Sandra Torres (sato) Manana Lun-Jue+Sab
  ('sato@pulsia.com','florez042@pulsia.com',     '2026-08-03 08:00','Atendida',    'Limpieza dental completa.'),
  ('sato@pulsia.com','bautista043@pulsia.com',   '2026-08-04 08:30','Atendida',    'Extraccion molar impactado.'),
  ('sato@pulsia.com','mesa044@pulsia.com',       '2026-08-06 09:00','No_Asistio',  NULL),
  ('sato@pulsia.com','henao045@pulsia.com',      '2026-08-10 08:00','Atendida',    'Aplicacion de fluor.'),
  ('sato@pulsia.com','fajardo046@pulsia.com',    '2026-08-11 08:30','Programada',  NULL),
  ('sato@pulsia.com','mendez047@pulsia.com',     '2026-08-13 09:00','Programada',  NULL),
  ('sato@pulsia.com','navas048@pulsia.com',      '2026-08-15 08:00','Programada',  NULL),
  ('sato@pulsia.com','guerrero049@pulsia.com',   '2026-08-17 08:30','Programada',  NULL),
  ('sato@pulsia.com','salazar050@pulsia.com',    '2026-08-18 09:00','Programada',  NULL),
  ('sato@pulsia.com','arteaga051@pulsia.com',    '2026-08-20 08:00','Programada',  NULL),
  ('sato@pulsia.com','benitez052@pulsia.com',    '2026-08-22 08:30','Programada',  NULL),
  ('sato@pulsia.com','paredes053@pulsia.com',    '2026-08-24 09:00','Programada',  NULL),
  -- ODONTOLOGIA - Felipe Vargas (feva) Tarde Mar-Vie
  ('feva@pulsia.com','rincon054@pulsia.com',     '2026-08-04 14:00','Atendida',    'Tratamiento de caries multiples.'),
  ('feva@pulsia.com','correa055@pulsia.com',     '2026-08-05 14:30','Atendida',    'Endodoncia molar inferior.'),
  ('feva@pulsia.com','ibarra056@pulsia.com',     '2026-08-06 15:00','Cancelada',   'Conflicto de agenda.'),
  ('feva@pulsia.com','fuentes057@pulsia.com',    '2026-08-11 14:00','Programada',  NULL),
  ('feva@pulsia.com','montoya058@pulsia.com',    '2026-08-12 14:30','Programada',  NULL),
  ('feva@pulsia.com','cabra059@pulsia.com',      '2026-08-13 15:00','Programada',  NULL),
  ('feva@pulsia.com','solano060@pulsia.com',     '2026-08-18 14:00','Programada',  NULL),
  ('feva@pulsia.com','zapata061@pulsia.com',     '2026-08-19 14:30','Programada',  NULL),
  ('feva@pulsia.com','acosta062@pulsia.com',     '2026-08-25 15:00','Programada',  NULL),
  -- ODONTOLOGIA - Valentina Leon (vale) Completo Lun-Vie
  ('vale@pulsia.com','rocha063@pulsia.com',      '2026-08-03 07:30','Atendida',    'Blanqueamiento dental.'),
  ('vale@pulsia.com','duran064@pulsia.com',      '2026-08-03 14:00','Atendida',    'Control de ortodoncia.'),
  ('vale@pulsia.com','escobar065@pulsia.com',    '2026-08-04 08:00','Atendida',    'Radiografia panoramica.'),
  ('vale@pulsia.com','palacio066@pulsia.com',    '2026-08-05 09:00','Programada',  NULL),
  ('vale@pulsia.com','betancur067@pulsia.com',   '2026-08-06 14:30','Programada',  NULL),
  ('vale@pulsia.com','angel068@pulsia.com',      '2026-08-11 08:00','Programada',  NULL),
  ('vale@pulsia.com','casta069@pulsia.com',      '2026-08-12 14:00','Programada',  NULL),
  ('vale@pulsia.com','guzman070@pulsia.com',     '2026-08-13 09:30','Programada',  NULL),
  ('vale@pulsia.com','rojas071@pulsia.com',      '2026-08-18 08:00','Programada',  NULL),
  ('vale@pulsia.com','duque072@pulsia.com',      '2026-08-19 14:00','Programada',  NULL),
  -- CARDIOLOGIA - Andres Soto (anso) Manana Lun-Mie
  ('anso@pulsia.com','caro073@pulsia.com',       '2026-08-03 08:00','Atendida',    'Ecocardiograma interpretado. Leve hipertension.'),
  ('anso@pulsia.com','sanchez074@pulsia.com',    '2026-08-04 08:30','Atendida',    'Post infarto, control mensual.'),
  ('anso@pulsia.com','camacho075@pulsia.com',    '2026-08-05 09:00','No_Asistio',  NULL),
  ('anso@pulsia.com','leon076@pulsia.com',       '2026-08-10 08:00','Atendida',    'Holter de 24h, arritmia leve.'),
  ('anso@pulsia.com','neira077@pulsia.com',      '2026-08-11 08:30','Programada',  NULL),
  ('anso@pulsia.com','triana078@pulsia.com',     '2026-08-12 09:00','Programada',  NULL),
  ('anso@pulsia.com','galvis079@pulsia.com',     '2026-08-17 08:00','Programada',  NULL),
  ('anso@pulsia.com','saenz080@pulsia.com',      '2026-08-18 08:30','Programada',  NULL),
  ('anso@pulsia.com','celis081@pulsia.com',      '2026-08-19 09:00','Programada',  NULL),
  ('anso@pulsia.com','sandoval082@pulsia.com',   '2026-08-24 08:00','Programada',  NULL),
  ('anso@pulsia.com','pineda083@pulsia.com',     '2026-08-25 08:30','Programada',  NULL),
  -- CARDIOLOGIA - Claudia Munoz (clmu) Tarde Jue-Vie+Sab
  ('clmu@pulsia.com','camargo084@pulsia.com',    '2026-08-06 14:00','Atendida',    'Control lipidico. Colesterol elevado.'),
  ('clmu@pulsia.com','orozco085@pulsia.com',     '2026-08-08 08:00','Atendida',    'Revision de marcapasos.'),
  ('clmu@pulsia.com','villamizar086@pulsia.com', '2026-08-13 14:30','Programada',  NULL),
  ('clmu@pulsia.com','barrero087@pulsia.com',    '2026-08-14 14:00','Programada',  NULL),
  ('clmu@pulsia.com','herrera088@pulsia.com',    '2026-08-15 08:00','Programada',  NULL),
  ('clmu@pulsia.com','silva089@pulsia.com',      '2026-08-20 14:00','Programada',  NULL),
  ('clmu@pulsia.com','rubio090@pulsia.com',      '2026-08-21 14:30','Programada',  NULL),
  ('clmu@pulsia.com','mateus091@pulsia.com',     '2026-08-22 08:00','Programada',  NULL),
  ('clmu@pulsia.com','velasco092@pulsia.com',    '2026-08-27 14:00','Programada',  NULL),
  ('clmu@pulsia.com','posada093@pulsia.com',     '2026-08-28 14:30','Programada',  NULL),
  -- CARDIOLOGIA - Ricardo Castro (rica) Completo Lun-Vie
  ('rica@pulsia.com','pinto094@pulsia.com',      '2026-08-03 07:00','Atendida',    'Electrocardiograma. Normal.'),
  ('rica@pulsia.com','contreras095@pulsia.com',  '2026-08-03 14:00','Atendida',    'Dx: insuficiencia cardiaca leve.'),
  ('rica@pulsia.com','ceron096@pulsia.com',      '2026-08-04 07:30','Atendida',    'Control hipertension.'),
  ('rica@pulsia.com','roa097@pulsia.com',        '2026-08-05 08:00','No_Asistio',  NULL),
  ('rica@pulsia.com','puentes098@pulsia.com',    '2026-08-11 07:00','Programada',  NULL),
  ('rica@pulsia.com','tovar099@pulsia.com',      '2026-08-12 14:00','Programada',  NULL),
  ('rica@pulsia.com','pema@pulsia.com',          '2026-08-18 07:30','Programada',  NULL),
  ('rica@pulsia.com','luna001@pulsia.com',       '2026-08-19 08:00','Programada',  NULL),
  ('rica@pulsia.com','meza002@pulsia.com',       '2026-08-25 07:00','Programada',  NULL),
  ('rica@pulsia.com','sosa003@pulsia.com',       '2026-08-26 14:30','Programada',  NULL),
  -- PEDIATRIA - Lucia Bermudez (lube) Manana Lun-Vie
  ('lube@pulsia.com','vega004@pulsia.com',       '2026-08-03 08:00','Atendida',    'Vacunacion pentavalente.'),
  ('lube@pulsia.com','rios005@pulsia.com',       '2026-08-04 08:30','Atendida',    'Control de crecimiento, 3 anos.'),
  ('lube@pulsia.com','nino006@pulsia.com',       '2026-08-05 09:00','Atendida',    'Fiebre. Diagnostico: amigdalitis.'),
  ('lube@pulsia.com','ruiz007@pulsia.com',       '2026-08-11 08:00','Programada',  NULL),
  ('lube@pulsia.com','alba008@pulsia.com',       '2026-08-12 08:30','Programada',  NULL),
  ('lube@pulsia.com','mora009@pulsia.com',       '2026-08-13 09:00','Programada',  NULL),
  ('lube@pulsia.com','pino010@pulsia.com',       '2026-08-18 08:00','Programada',  NULL),
  ('lube@pulsia.com','cano011@pulsia.com',       '2026-08-19 08:30','Programada',  NULL),
  ('lube@pulsia.com','ovalle012@pulsia.com',     '2026-08-20 09:00','Programada',  NULL),
  -- PEDIATRIA - Daniel Gomez (dago) Tarde Lun-Jue
  ('dago@pulsia.com','cruz013@pulsia.com',       '2026-08-03 13:30','Atendida',    'Control mensual, desarrollo normal.'),
  ('dago@pulsia.com','leal014@pulsia.com',       '2026-08-04 14:00','Atendida',    'Diagnostico: bronquitis.'),
  ('dago@pulsia.com','ferro015@pulsia.com',      '2026-08-06 14:30','Cancelada',   NULL),
  ('dago@pulsia.com','daza016@pulsia.com',       '2026-08-11 13:30','Programada',  NULL),
  ('dago@pulsia.com','perez017@pulsia.com',      '2026-08-12 14:00','Programada',  NULL),
  ('dago@pulsia.com','gil018@pulsia.com',        '2026-08-13 14:30','Programada',  NULL),
  ('dago@pulsia.com','lara019@pulsia.com',       '2026-08-17 13:30','Programada',  NULL),
  ('dago@pulsia.com','baez020@pulsia.com',       '2026-08-18 14:00','Programada',  NULL),
  ('dago@pulsia.com','reyes021@pulsia.com',      '2026-08-19 14:30','Programada',  NULL),
  -- PEDIATRIA - Paula Ramirez (para) Completo Lun-Sab
  ('para@pulsia.com','olmos022@pulsia.com',      '2026-08-03 08:00','Atendida',    'Revision post-vacuna. Fiebre leve.'),
  ('para@pulsia.com','patino023@pulsia.com',     '2026-08-03 14:30','Atendida',    'Seguimiento peso y talla.'),
  ('para@pulsia.com','ossa024@pulsia.com',       '2026-08-04 09:00','Atendida',    'Alergia alimentaria detectada.'),
  ('para@pulsia.com','arias025@pulsia.com',      '2026-08-05 09:30','No_Asistio',  NULL),
  ('para@pulsia.com','rico026@pulsia.com',       '2026-08-08 09:00','Atendida',    'Control escolar. Normal.'),
  ('para@pulsia.com','suarez027@pulsia.com',     '2026-08-11 08:30','Programada',  NULL),
  ('para@pulsia.com','vera028@pulsia.com',       '2026-08-12 14:00','Programada',  NULL),
  ('para@pulsia.com','nieto029@pulsia.com',      '2026-08-15 09:00','Programada',  NULL),
  ('para@pulsia.com','serrano030@pulsia.com',    '2026-08-17 08:00','Programada',  NULL),
  ('para@pulsia.com','parra031@pulsia.com',      '2026-08-18 09:30','Programada',  NULL),
  -- GINECOLOGIA - Camila Morales (camo) Manana Lun-Vie
  ('camo@pulsia.com','gomez032@pulsia.com',      '2026-08-03 08:00','Atendida',    'Control prenatal 20 semanas.'),
  ('camo@pulsia.com','bolivar033@pulsia.com',    '2026-08-04 08:30','Atendida',    'Citologia de control.'),
  ('camo@pulsia.com','vargas034@pulsia.com',     '2026-08-05 09:00','Atendida',    'Revision DIU.'),
  ('camo@pulsia.com','casas035@pulsia.com',      '2026-08-06 08:00','No_Asistio',  NULL),
  ('camo@pulsia.com','leon036@pulsia.com',       '2026-08-11 08:30','Programada',  NULL),
  ('camo@pulsia.com','molina037@pulsia.com',     '2026-08-12 09:00','Programada',  NULL),
  ('camo@pulsia.com','torres038@pulsia.com',     '2026-08-13 08:00','Programada',  NULL),
  ('camo@pulsia.com','agudelo039@pulsia.com',    '2026-08-18 08:30','Programada',  NULL),
  ('camo@pulsia.com','duarte040@pulsia.com',     '2026-08-19 09:00','Programada',  NULL),
  ('camo@pulsia.com','ospina041@pulsia.com',     '2026-08-20 08:00','Programada',  NULL),
  -- GINECOLOGIA - Sofia Rios (sori) Tarde Mar-Sab
  ('sori@pulsia.com','florez042@pulsia.com',     '2026-08-04 14:00','Atendida',    'Tratamiento sindrome de ovario poliquistico.'),
  ('sori@pulsia.com','bautista043@pulsia.com',   '2026-08-05 14:30','Atendida',    'Control hormonal.'),
  ('sori@pulsia.com','mesa044@pulsia.com',       '2026-08-06 15:00','Cancelada',   NULL),
  ('sori@pulsia.com','henao045@pulsia.com',      '2026-08-11 14:00','Programada',  NULL),
  ('sori@pulsia.com','fajardo046@pulsia.com',    '2026-08-12 14:30','Programada',  NULL),
  ('sori@pulsia.com','mendez047@pulsia.com',     '2026-08-15 08:00','Programada',  NULL),
  ('sori@pulsia.com','navas048@pulsia.com',      '2026-08-18 14:00','Programada',  NULL),
  ('sori@pulsia.com','guerrero049@pulsia.com',   '2026-08-19 14:30','Programada',  NULL),
  ('sori@pulsia.com','salazar050@pulsia.com',    '2026-08-22 08:00','Programada',  NULL),
  -- GINECOLOGIA - Nicolas Olarte (niol) Completo Mie-Vie
  ('niol@pulsia.com','arteaga051@pulsia.com',    '2026-08-05 07:00','Atendida',    'Colposcopia. Normal.'),
  ('niol@pulsia.com','benitez052@pulsia.com',    '2026-08-05 14:00','Atendida',    'Consulta planificacion familiar.'),
  ('niol@pulsia.com','paredes053@pulsia.com',    '2026-08-06 07:30','Atendida',    'Diagnostico: endometriosis leve.'),
  ('niol@pulsia.com','rincon054@pulsia.com',     '2026-08-12 07:00','Programada',  NULL),
  ('niol@pulsia.com','correa055@pulsia.com',     '2026-08-13 14:00','Programada',  NULL),
  ('niol@pulsia.com','ibarra056@pulsia.com',     '2026-08-14 07:30','Programada',  NULL),
  ('niol@pulsia.com','fuentes057@pulsia.com',    '2026-08-19 07:00','Programada',  NULL),
  ('niol@pulsia.com','montoya058@pulsia.com',    '2026-08-20 14:00','Programada',  NULL),
  ('niol@pulsia.com','cabra059@pulsia.com',      '2026-08-21 07:30','Programada',  NULL),
  -- DERMATOLOGIA - Isabel Pena (ispe) Manana Lun-Jue
  ('ispe@pulsia.com','solano060@pulsia.com',     '2026-08-03 08:00','Atendida',    'Diagnostico: dermatitis atopica.'),
  ('ispe@pulsia.com','zapata061@pulsia.com',     '2026-08-04 08:30','Atendida',    'Extirpacion lunar benigno.'),
  ('ispe@pulsia.com','acosta062@pulsia.com',     '2026-08-06 09:00','No_Asistio',  NULL),
  ('ispe@pulsia.com','rocha063@pulsia.com',      '2026-08-10 08:00','Atendida',    'Control psoriasis, mejoria.'),
  ('ispe@pulsia.com','duran064@pulsia.com',      '2026-08-11 08:30','Programada',  NULL),
  ('ispe@pulsia.com','escobar065@pulsia.com',    '2026-08-12 09:00','Programada',  NULL),
  ('ispe@pulsia.com','palacio066@pulsia.com',    '2026-08-13 08:00','Programada',  NULL),
  ('ispe@pulsia.com','betancur067@pulsia.com',   '2026-08-17 08:30','Programada',  NULL),
  ('ispe@pulsia.com','angel068@pulsia.com',      '2026-08-18 09:00','Programada',  NULL),
  ('ispe@pulsia.com','casta069@pulsia.com',      '2026-08-20 08:00','Programada',  NULL),
  -- DERMATOLOGIA - Hernan Ramos (hera) Tarde Lun-Vie
  ('hera@pulsia.com','guzman070@pulsia.com',     '2026-08-03 14:00','Atendida',    'Acne severo. Isotretinoina ordenada.'),
  ('hera@pulsia.com','rojas071@pulsia.com',      '2026-08-04 14:30','Atendida',    'Control de rosácea.'),
  ('hera@pulsia.com','duque072@pulsia.com',      '2026-08-05 15:00','Cancelada',   NULL),
  ('hera@pulsia.com','caro073@pulsia.com',       '2026-08-11 14:00','Programada',  NULL),
  ('hera@pulsia.com','sanchez074@pulsia.com',    '2026-08-12 14:30','Programada',  NULL),
  ('hera@pulsia.com','camacho075@pulsia.com',    '2026-08-13 15:00','Programada',  NULL),
  ('hera@pulsia.com','leon076@pulsia.com',       '2026-08-18 14:00','Programada',  NULL),
  ('hera@pulsia.com','neira077@pulsia.com',      '2026-08-19 14:30','Programada',  NULL),
  ('hera@pulsia.com','triana078@pulsia.com',     '2026-08-20 15:00','Programada',  NULL),
  ('hera@pulsia.com','galvis079@pulsia.com',     '2026-08-25 14:00','Programada',  NULL),
  -- DERMATOLOGIA - Nives Villa (nivi) Completo Lun-Sab
  ('nivi@pulsia.com','saenz080@pulsia.com',      '2026-08-03 08:00','Atendida',    'Manejo de urticaria cronica.'),
  ('nivi@pulsia.com','celis081@pulsia.com',      '2026-08-03 14:30','Atendida',    'Control melasma. Respuesta positiva.'),
  ('nivi@pulsia.com','sandoval082@pulsia.com',   '2026-08-04 09:00','Atendida',    'Diagnostico: alopecia areata.'),
  ('nivi@pulsia.com','pineda083@pulsia.com',     '2026-08-05 08:30','No_Asistio',  NULL),
  ('nivi@pulsia.com','camargo084@pulsia.com',    '2026-08-08 08:00','Atendida',    'Extirpacion verruga plantar.'),
  ('nivi@pulsia.com','orozco085@pulsia.com',     '2026-08-11 08:00','Programada',  NULL),
  ('nivi@pulsia.com','villamizar086@pulsia.com', '2026-08-12 14:30','Programada',  NULL),
  ('nivi@pulsia.com','barrero087@pulsia.com',    '2026-08-15 08:30','Programada',  NULL),
  ('nivi@pulsia.com','herrera088@pulsia.com',    '2026-08-17 08:00','Programada',  NULL),
  ('nivi@pulsia.com','silva089@pulsia.com',      '2026-08-18 14:00','Programada',  NULL),
  -- PSICOLOGIA - Alejandro Cordoba (alco) Manana Lun-Vie
  ('alco@pulsia.com','rubio090@pulsia.com',      '2026-08-03 08:00','Atendida',    'Terapia cognitivo-conductual. Sesion 3.'),
  ('alco@pulsia.com','mateus091@pulsia.com',     '2026-08-04 08:30','Atendida',    'Manejo de ansiedad social.'),
  ('alco@pulsia.com','velasco092@pulsia.com',    '2026-08-05 09:00','Atendida',    'Sesion inicial de evaluacion.'),
  ('alco@pulsia.com','posada093@pulsia.com',     '2026-08-06 08:00','No_Asistio',  NULL),
  ('alco@pulsia.com','pinto094@pulsia.com',      '2026-08-11 08:30','Programada',  NULL),
  ('alco@pulsia.com','contreras095@pulsia.com',  '2026-08-12 09:00','Programada',  NULL),
  ('alco@pulsia.com','ceron096@pulsia.com',      '2026-08-13 08:00','Programada',  NULL),
  ('alco@pulsia.com','roa097@pulsia.com',        '2026-08-18 08:30','Programada',  NULL),
  ('alco@pulsia.com','puentes098@pulsia.com',    '2026-08-19 09:00','Programada',  NULL),
  ('alco@pulsia.com','tovar099@pulsia.com',      '2026-08-20 08:00','Programada',  NULL),
  -- PSICOLOGIA - Gustavo Salcedo (gusa) Tarde Lun-Jue+Sab
  ('gusa@pulsia.com','pema@pulsia.com',          '2026-08-03 14:00','Atendida',    'Terapia de pareja, sesion 1.'),
  ('gusa@pulsia.com','luna001@pulsia.com',       '2026-08-04 14:30','Atendida',    'Duelo. Segunda sesion.'),
  ('gusa@pulsia.com','meza002@pulsia.com',       '2026-08-06 15:00','Cancelada',   NULL),
  ('gusa@pulsia.com','sosa003@pulsia.com',       '2026-08-08 08:00','Atendida',    'TDAH adulto. Evaluacion inicial.'),
  ('gusa@pulsia.com','vega004@pulsia.com',       '2026-08-11 14:00','Programada',  NULL),
  ('gusa@pulsia.com','rios005@pulsia.com',       '2026-08-12 14:30','Programada',  NULL),
  ('gusa@pulsia.com','nino006@pulsia.com',       '2026-08-13 15:00','Programada',  NULL),
  ('gusa@pulsia.com','ruiz007@pulsia.com',       '2026-08-18 14:00','Programada',  NULL),
  ('gusa@pulsia.com','alba008@pulsia.com',       '2026-08-19 14:30','Programada',  NULL),
  ('gusa@pulsia.com','mora009@pulsia.com',       '2026-08-22 08:00','Programada',  NULL),
  -- PSICOLOGIA - Angela Guerrero (angu) Completo Mar-Vie
  ('angu@pulsia.com','pino010@pulsia.com',       '2026-08-04 07:30','Atendida',    'Fobia especifica. Exposicion gradual.'),
  ('angu@pulsia.com','cano011@pulsia.com',       '2026-08-04 14:00','Atendida',    'Trastorno de panico. Psicoeducacion.'),
  ('angu@pulsia.com','ovalle012@pulsia.com',     '2026-08-05 08:00','Atendida',    'Depresion leve. Inicio tratamiento.'),
  ('angu@pulsia.com','cruz013@pulsia.com',       '2026-08-06 09:00','Programada',  NULL),
  ('angu@pulsia.com','leal014@pulsia.com',       '2026-08-11 07:30','Programada',  NULL),
  ('angu@pulsia.com','ferro015@pulsia.com',      '2026-08-12 14:00','Programada',  NULL),
  ('angu@pulsia.com','daza016@pulsia.com',       '2026-08-13 08:30','Programada',  NULL),
  ('angu@pulsia.com','perez017@pulsia.com',      '2026-08-18 07:30','Programada',  NULL),
  ('angu@pulsia.com','gil018@pulsia.com',        '2026-08-19 14:00','Programada',  NULL),
  ('angu@pulsia.com','lara019@pulsia.com',       '2026-08-20 08:00','Programada',  NULL)
) AS c(correo_esp, correo_pac, fi, est, nota)
JOIN agendamiento_especialista e ON TRUE
JOIN agendamiento_customuser ue ON e.usuario_id = ue.id AND ue.correo = c.correo_esp
JOIN agendamiento_customuser up ON up.correo = c.correo_pac
JOIN agendamiento_paciente p ON p.usuario_id = up.id;

-- FIN DEL SCRIPT
-- Total esperado: ~240 citas | 100 pacientes | 21 especialistas | 7 especialidades | 21 consultorios

# 🎨 Guía de Diseño, Tipografía y Paleta de Colores — Pulsia

Este documento centraliza el Sistema de Diseño (*Design System*) visual de **Pulsia**, incluyendo las fuentes tipográficas, tokens de color en Tailwind CSS, componentes visuales e indicadores de estado.

---

## 🔤 1. Tipografía Principal

Pulsia utiliza la familia tipográfica moderna **Inter** importada desde Google Fonts para lograr máxima legibilidad clínica y estética internacional.

- **Fuente:** `'Inter', system-ui, -apple-system, sans-serif`
- **Importación CDN:**
  ```html
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  ```
- **Escala de Pesos:**
  - `Font Regular (400)`: Textos explicativos, descripciones y cuerpo general.
  - `Font Medium (500)`: Etiquetas secundarias, horas y badges informativos.
  - `Font SemiBold (600)`: Títulos de tarjetas, nombres de usuarios y campos de formulario.
  - `Font Bold (700 / 800)`: Encabezados principales, estados resaltados y botones primarios.

---

## 🎨 2. Paleta de Colores (Tokens de Tailwind CSS)

El tema visual se define mediante tokens personalizados en `tailwind.config` dentro de `base.html`:

### 🔹 Azul Primario Institucional (`primary`)
Color dominante para botones principales, marcas de calendario y branding.

| Nombre Token | Código Hexadecimal | Uso Recomendado |
| :--- | :--- | :--- |
| `primary-50` | `#eef4fc` | Fondos de selección, items activos y resúmenes. |
| `primary-100` | `#cfe0f5` | Bordes suaves y avatares secundarios. |
| `primary-200` | `#9fc1eb` | Subtítulos sobre tarjetas oscuras. |
| `primary-500` *(DEFAULT)* | `#0056b3` | Botones principales, enlaces y bordes activos. |
| `primary-600` | `#00469a` | Estado Hover de botones primarios. |
| `primary-700` | `#003680` | Gradientes de tarjetas oscuras principales. |

### 🍏 Fondos y Superficies Neutras
- **Superficie de fondo (`bg-surface`):** `#f7f9fb` (Gris frío de alta pulcritud).
- **Tarjetas y contenedores (`bg-white` / `bg-card`):** `#ffffff` / `#f2f4f6`.
- **Texto principal (`text-ink`):** `#1a1c1e` (Negro carbón suave para reducir fatiga visual).
- **Texto secundario (`text-muted`):** `#44474a` (Gris neutro de lectura).

---

## 🚦 3. Colores Semánticos por Estado de Citas

| Estado de la Cita | Color de Fondo | Color de Texto y Borde | Código Hex |
| :--- | :--- | :--- | :--- |
| **Programada** | `bg-blue-50` | `text-blue-600 border-blue-200` | `#0056b3` |
| **En Sala (Asistió)** | `bg-amber-50` | `text-amber-700 border-amber-200` | `#d97706` |
| **Atendida** | `bg-emerald-50` | `text-emerald-700 border-emerald-200` | `#059669` |
| **No Asistió** | `bg-red-50` | `text-red-700 border-red-200` | `#dc2626` |
| **Pendiente de Reubicación** | `bg-purple-50` | `text-purple-700 border-purple-200` | `#7c3aed` |
| **Cancelada** | `bg-gray-100` | `text-gray-600 border-gray-200` | `#6b7280` |

---

## 🔘 4. Componentes y Botones de la Interfaz

### Botones Principales
- **Botón Primario:** `bg-primary hover:bg-primary-600 text-white font-bold rounded-xl shadow-md`
- **Botón Positivo (Asistió):** `bg-emerald-50 text-emerald-700 hover:bg-emerald-600 hover:text-white border border-emerald-200 font-bold rounded-xl`
- **Botón Negativo (No Asistió):** `bg-red-50 text-red-700 hover:bg-red-600 hover:text-white border border-red-200 font-bold rounded-xl`
- **Botón Secundario / Cancelar:** `border border-gray-200 text-muted hover:bg-surface font-semibold rounded-xl`

### Sombra de Tarjetas (*Elevation*)
```css
boxShadow: {
  'card': '0 1px 3px 0 rgba(0,0,0,.06), 0 1px 2px -1px rgba(0,0,0,.04)',
  'card-hover': '0 10px 25px -5px rgba(0,86,179,.12), 0 4px 10px -6px rgba(0,86,179,.08)'
}
```

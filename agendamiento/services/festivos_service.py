"""
Servicio para detección y cálculo de días festivos en Colombia (Ley Emiliani)
Permite inhabilitar días feriados nacionales en la agenda médica (HU08 / RF05).
"""
import datetime

# Festivos fijos y calculados aproximados para Colombia (Ley Emiliani)
FESTIVOS_FIJOS = [
    (1, 1),   # Año Nuevo
    (5, 1),   # Día del Trabajo
    (7, 20),  # Día de la Independencia
    (8, 7),   # Batalla de Boyacá
    (12, 8),  # Inmaculada Concepción
    (12, 25), # Navidad
]

# Días trasladables al siguiente lunes si no caen en lunes (Ley Emiliani)
FESTIVOS_EMILIANI = [
    (1, 6),   # Reyes Magos
    (3, 19),  # San José
    (6, 29),  # San Pedro y San Pablo
    (8, 15),  # Asunción de la Virgen
    (10, 12), # Día de la Raza
    (11, 1),  # Todos los Santos
    (11, 11), # Independencia de Cartagena
]

def es_dia_festivo(fecha: datetime.date) -> bool:
    """
    Retorna True si la fecha especificada es un día festivo en Colombia.
    """
    mes, dia = fecha.month, fecha.day
    
    # 1. Festivos fijos
    if (mes, dia) in FESTIVOS_FIJOS:
        return True

    # 2. Festivos trasladables (Si caen en cualquier día != Lunes, se trasladan al Lunes)
    for f_mes, f_dia in FESTIVOS_EMILIANI:
        try:
            f_fecha = datetime.date(fecha.year, f_mes, f_dia)
        except ValueError:
            continue
        
        # Si la fecha original cae en Lunes (weekday() == 0), se mantiene ese día
        if f_fecha.weekday() == 0:
            festivo_celebrado = f_fecha
        else:
            # Se traslada al siguiente lunes
            dias_hasta_lunes = (7 - f_fecha.weekday()) % 7
            if dias_hasta_lunes == 0:
                dias_hasta_lunes = 7
            festivo_celebrado = f_fecha + datetime.timedelta(days=dias_hasta_lunes)

        if fecha == festivo_celebrado:
            return True

    return False

"""
Servicio para el cálculo y consulta de Días Festivos en Colombia (Ley 51 de 1983 - Ley Emiliani).
Proporciona la lista de festivos nacionales para cualquier año y verifica si una fecha dada es festivo.
"""

from datetime import date, timedelta
import urllib.request
import json
import logging

logger = logging.getLogger(__name__)

def calcular_pascua(year: int) -> date:
    """Calcula el Domingo de Pascua utilizando el algoritmo de Meeus/Jones/Butcher."""
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)

def mover_a_lunes(fecha: date) -> date:
    """Si la fecha no cae un lunes (weekday != 0), se traslada al siguiente lunes (Ley Emiliani)."""
    dias_para_lunes = (7 - fecha.weekday()) % 7
    if dias_para_lunes > 0:
        return fecha + timedelta(days=dias_para_lunes)
    return fecha

def obtener_festivos_colombia(year: int) -> list[dict]:
    """
    Retorna la lista completa de festivos oficiales en Colombia para el año indicado.
    Cada elemento es un dict: {'fecha': 'YYYY-MM-DD', 'date': date, 'nombre': 'Nombre del Festivo'}
    """
    pascua = calcular_pascua(year)

    # 1. Festivos Fijos (No se mueven)
    festivos = [
        {'date': date(year, 1, 1), 'nombre': 'Año Nuevo'},
        {'date': date(year, 5, 1), 'nombre': 'Día del Trabajo'},
        {'date': date(year, 7, 20), 'nombre': 'Día de la Independencia'},
        {'date': date(year, 8, 7), 'nombre': 'Batalla de Boyacá'},
        {'date': date(year, 12, 8), 'nombre': 'Inmaculada Concepción'},
        {'date': date(year, 12, 25), 'nombre': 'Navidad'},
    ]

    # 2. Festivos movibles al siguiente lunes (Ley Emiliani)
    emiliani_fijos = [
        (date(year, 1, 6), 'Reyes Magos'),
        (date(year, 3, 19), 'Día de San José'),
        (date(year, 6, 29), 'San Pedro y San Pablo'),
        (date(year, 8, 15), 'Asunción de la Virgen'),
        (date(year, 10, 12), 'Día de la Raza'),
        (date(year, 11, 1), 'Día de Todos los Santos'),
        (date(year, 11, 11), 'Independencia de Cartagena'),
    ]
    for fecha_base, nombre in emiliani_fijos:
        festivos.append({'date': mover_a_lunes(fecha_base), 'nombre': nombre})

    # 3. Festivos vinculados a la Semana Santa
    jueves_santo = pascua - timedelta(days=3)
    viernes_santo = pascua - timedelta(days=2)
    ascension = mover_a_lunes(pascua + timedelta(days=43))
    corpus_christi = mover_a_lunes(pascua + timedelta(days=64))
    sagrado_corazon = mover_a_lunes(pascua + timedelta(days=71))

    festivos.extend([
        {'date': jueves_santo, 'nombre': 'Jueves Santo'},
        {'date': viernes_santo, 'nombre': 'Viernes Santo'},
        {'date': ascension, 'nombre': 'Ascensión del Señor'},
        {'date': corpus_christi, 'nombre': 'Corpus Christi'},
        {'date': sagrado_corazon, 'nombre': 'Sagrado Corazón de Jesús'},
    ])

    # Formatear la salida y ordenar por fecha
    festivos_ordenados = sorted(festivos, key=lambda x: x['date'])
    for f in festivos_ordenados:
        f['fecha'] = f['date'].strftime('%Y-%m-%d')

    return festivos_ordenados

def es_dia_festivo(fecha_evaluar: date) -> tuple[bool, str]:
    """
    Verifica si una fecha es festivo nacional en Colombia.
    Retorna (True, 'Nombre Festivo') o (False, '').
    """
    festivos = obtener_festivos_colombia(fecha_evaluar.year)
    for f in festivos:
        if f['date'] == fecha_evaluar:
            return True, f['nombre']
    return False, ''

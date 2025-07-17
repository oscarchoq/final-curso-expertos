# configuracion.py
"""
Configuraciones y constantes del juego de damas.
"""

# --- Configuración del Juego de Damas ---
TABLERO_DIM = 8  # Dimensión del tablero (8 para estándar, 10 para internacional)

# Representación de jugadores y piezas
JUGADOR_BLANCO = "B"
JUGADOR_NEGRO = "N"
CELDA_VACIA = None

# Representación de damas
DAMA_BLANCA = "DB"
DAMA_NEGRA = "DN"

# --- Niveles de Dificultad ---
NIVELES_DIFICULTAD = {
    1: {
        "nombre": "Principiante",
        "profundidad": 1,
        "error_probabilidad": 0.3,  # 30% de probabilidad de hacer un movimiento subóptimo
        "descripcion": "IA muy básica, comete errores frecuentes"
    },
    2: {
        "nombre": "Intermedio",
        "profundidad": 3,
        "error_probabilidad": 0.1,  # 10% de probabilidad de error
        "descripcion": "IA competente, pocos errores"
    },
    3: {
        "nombre": "Experto",
        "profundidad": 5,
        "error_probabilidad": 0.0,  # Sin errores intencionales
        "descripcion": "IA máxima, juego perfecto"
    }
}

# Valores para la función de evaluación
VALOR_PEON = 10
VALOR_DAMA = 80
VALOR_GANADOR = 1000
VALOR_MOVILIDAD = 0.5
VALOR_AVANCE = 1.0
VALOR_CENTRO = 2.0

# busqueda.py
import math
import copy

# --- Configuración del Juego de Damas Chinas ---
TABLERO_DIM = 8 # Puedes cambiar esto (8 para estándar, 10 para internacional)

JUGADOR_BLANCO = "B"  # Representa las piezas blancas
JUGADOR_NEGRO = "N"  # Representa las piezas negras
CELDA_VACIA = None    # Representa una celda vacía

# Se usará para identificar la "dama" o "reina"
DAMA_BLANCA = "DB"
DAMA_NEGRA = "DN"

def tablero_inicial():
    """
    Inicializa un tablero de Damas Chinas con la disposición estándar.
    Las fichas se colocan solo en las casillas oscuras (donde (fila + columna) % 2 != 0).
    """
    tablero = [[CELDA_VACIA for _ in range(TABLERO_DIM)] for _ in range(TABLERO_DIM)]

    for r in range(TABLERO_DIM):
        for c in range(TABLERO_DIM):
            if (r + c) % 2 != 0: # Si la casilla es "oscura"
                if r < (TABLERO_DIM // 2) - 1: # Filas iniciales para el jugador NEGRO
                    tablero[r][c] = JUGADOR_NEGRO
                elif r >= (TABLERO_DIM // 2) + 1: # Filas iniciales para el jugador BLANCO
                    tablero[r][c] = JUGADOR_BLANCO
    return tablero

def obtener_jugador_oponente(jugador):
    """
    Retorna el jugador opuesto.
    """
    return JUGADOR_NEGRO if jugador == JUGADOR_BLANCO else JUGADOR_BLANCO


def movimientos_disponibles(tablero, jugador_actual):
    """
    Retorna un conjunto de todos los movimientos (origen, destino) válidos para el jugador_actual.
    En Damas Chinas, las capturas NO son obligatorias. Se devuelven tanto movimientos normales como saltos.
    """
    todos_los_movimientos = set()

    for r in range(TABLERO_DIM):
        for c in range(TABLERO_DIM):
            pieza = tablero[r][c]
            
            es_pieza_actual = False
            es_dama = False
            if jugador_actual == JUGADOR_BLANCO:
                if pieza == JUGADOR_BLANCO: es_pieza_actual = True
                if pieza == DAMA_BLANCA: es_pieza_actual = True; es_dama = True
            elif jugador_actual == JUGADOR_NEGRO:
                if pieza == JUGADOR_NEGRO: es_pieza_actual = True
                if pieza == DAMA_NEGRA: es_pieza_actual = True; es_dama = True
            
            if es_pieza_actual:
                # Añadir movimientos normales
                if not es_dama: # Peón
                    todos_los_movimientos.update(_obtener_movimientos_normales_peon(tablero, (r, c), jugador_actual))
                else: # Dama
                    todos_los_movimientos.update(_obtener_movimientos_normales_dama(tablero, (r, c)))
                
                # Añadir movimientos de salto (no de captura en Damas Chinas, solo "pasar por encima")
                todos_los_movimientos.update(_obtener_saltos_posibles(tablero, (r, c), jugador_actual, es_dama))
                
    return todos_los_movimientos

def _obtener_movimientos_normales_peon(tablero, origen, jugador):
    """
    Retorna los movimientos normales (no de salto) para un peón.
    """
    movimientos = set()
    r, c = origen
    
    # Dirección de avance para peones
    if jugador == JUGADOR_BLANCO:
        direcciones_avance = [(-1, -1), (-1, 1)] # Hacia arriba (filas decrecientes)
    else: # JUGADOR_NEGRO
        direcciones_avance = [(1, -1), (1, 1)] # Hacia abajo (filas crecientes)

    for dr, dc in direcciones_avance:
        new_r, new_c = r + dr, c + dc
        if 0 <= new_r < TABLERO_DIM and 0 <= new_c < TABLERO_DIM:
            if (new_r + new_c) % 2 != 0 and tablero[new_r][new_c] == CELDA_VACIA: # Mover a casilla oscura vacía
                movimientos.add((origen, (new_r, new_c)))
    return movimientos

def _obtener_movimientos_normales_dama(tablero, origen):
    """
    Retorna los movimientos normales (no de salto) para una dama.
    Una dama puede moverse cualquier número de casillas diagonales en cualquier dirección.
    """
    movimientos = set()
    r, c = origen
    direcciones = [(-1, -1), (-1, 1), (1, -1), (1, 1)] # Todas las diagonales

    for dr, dc in direcciones:
        for i in range(1, TABLERO_DIM): # Intentar hasta el borde del tablero
            new_r, new_c = r + dr * i, c + dc * i
            if 0 <= new_r < TABLERO_DIM and 0 <= new_c < TABLERO_DIM:
                if tablero[new_r][new_c] == CELDA_VACIA:
                    movimientos.add((origen, (new_r, new_c)))
                else: # Bloqueado por otra pieza
                    break
            else: # Fuera del tablero
                break
    return movimientos


def _obtener_saltos_posibles(tablero, origen, jugador, es_dama):
    """
    Obtiene todos los saltos posibles para una pieza específica.
    En Damas Chinas, el salto es sobre CUALQUIER pieza adyacente a una casilla VACÍA directamente detrás de ella.
    La pieza saltada NO se captura.
    """
    saltos = set()
    r, c = origen
    
    direcciones = [(-1, -1), (-1, 1), (1, -1), (1, 1)] # Todas las diagonales

    for dr, dc in direcciones:
        if not es_dama: # Peones solo pueden saltar hacia adelante
            if (jugador == JUGADOR_BLANCO and dr == 1) or \
               (jugador == JUGADOR_NEGRO and dr == -1):
                continue # Si es peón, no puede saltar hacia atrás

        # Casilla sobre la que se salta (debe contener una pieza)
        salto_r, salto_c = r + dr, c + dc
        # Casilla de destino (debe estar vacía)
        destino_r, destino_c = r + 2 * dr, c + 2 * dc

        if (0 <= salto_r < TABLERO_DIM and 0 <= salto_c < TABLERO_DIM and
            0 <= destino_r < TABLERO_DIM and 0 <= destino_c < TABLERO_DIM):
            
            # Si hay una pieza en la casilla de salto y el destino está vacío
            if tablero[salto_r][salto_c] is not CELDA_VACIA and tablero[destino_r][destino_c] == CELDA_VACIA:
                if (destino_r + destino_c) % 2 != 0: # Asegurarse que el destino es una casilla oscura
                    saltos.add((origen, (destino_r, destino_c)))
                    # Nota: La lógica para cadenas de saltos múltiples en Damas Chinas
                    # (donde se puede seguir saltando sobre múltiples piezas en una dirección)
                    # es más compleja y no está implementada en esta versión.
        
    return saltos


def aplicar_movimiento(tablero, movimiento):
    """
    Aplica un movimiento (origen, destino) al tablero y devuelve un nuevo tablero.
    En Damas Chinas, las piezas NO se capturan (no se eliminan del tablero al ser saltadas).
    """
    nuevo_tablero = copy.deepcopy(tablero)
    (origen_r, origen_c), (destino_r, destino_c) = movimiento

    pieza_movida = nuevo_tablero[origen_r][origen_c]
    
    # Mover la pieza
    nuevo_tablero[destino_r][destino_c] = pieza_movida
    nuevo_tablero[origen_r][origen_c] = CELDA_VACIA

    # Si la diferencia entre las filas o columnas de origen y destino es 2,
    # significa que se ha realizado un salto, y la pieza intermedia debe ser "capturada".
    if abs(origen_r - destino_r) == 2 or abs(origen_c - destino_c) == 2:
        # Calcular la posición de la pieza capturada
        capturada_r = (origen_r + destino_r) // 2
        capturada_c = (origen_c + destino_c) // 2
        nuevo_tablero[capturada_r][capturada_c] = CELDA_VACIA # Eliminar la pieza capturada

    # Lógica de coronación (promoción a Dama)
    if pieza_movida == JUGADOR_BLANCO and destino_r == 0: # Blanco llega a la primera fila del oponente
        nuevo_tablero[destino_r][destino_c] = DAMA_BLANCA
    elif pieza_movida == JUGADOR_NEGRO and destino_r == TABLERO_DIM - 1: # Negro llega a la última fila del oponente
        nuevo_tablero[destino_r][destino_c] = DAMA_NEGRA

    return nuevo_tablero

def determinar_ganador(tablero, jugador_actual):
    """
    Determina si hay un ganador según las reglas simplificadas de Damas Chinas para este juego.
    Un jugador gana si el oponente no tiene más piezas o no tiene movimientos válidos.
    (La condición completa de victoria en Damas Chinas reales es mover todas las piezas a la zona de meta opuesta).
    """
    piezas_blancas = sum(1 for r in range(TABLERO_DIM) for c in range(TABLERO_DIM) if tablero[r][c] in [JUGADOR_BLANCO, DAMA_BLANCA])
    piezas_negras = sum(1 for r in range(TABLERO_DIM) for c in range(TABLERO_DIM) if tablero[r][c] in [JUGADOR_NEGRO, DAMA_NEGRA])

    if piezas_blancas == 0: # Si las blancas no tienen piezas, las negras ganan.
        return JUGADOR_NEGRO
    if piezas_negras == 0: # Si las negras no tienen piezas, las blancas ganan.
        return JUGADOR_BLANCO
    
    # Si el jugador actual no tiene movimientos válidos, el oponente gana.
    # Esto puede indicar un "ahogado" o simplemente que no puede moverse.
    if not movimientos_disponibles(tablero, jugador_actual):
        return obtener_jugador_oponente(jugador_actual)
    
    return None # No hay ganador todavía

def es_final(tablero, jugador_actual):
    """
    Verifica si el juego ha terminado.
    """
    return determinar_ganador(tablero, jugador_actual) is not None

def calcular_utilidad(tablero, jugador_para_evaluar):
    """
    Calcula la "utilidad" o valor heurístico del tablero para el algoritmo Minimax.
    Valor positivo significa ventaja para BLANCO, negativo para NEGRO.
    """
    ganador = determinar_ganador(tablero, jugador_para_evaluar)
    if ganador == JUGADOR_BLANCO:
        return 1000 # Blanco gana (valor alto)
    elif ganador == JUGADOR_NEGRO:
        return -1000 # Negro gana (valor bajo)
    
    score_blanco = 0
    score_negro = 0

    for r in range(TABLERO_DIM):
        for c in range(TABLERO_DIM):
            pieza = tablero[r][c]
            if pieza == JUGADOR_BLANCO:
                score_blanco += 10  # Valor base para peón blanco
                score_blanco += (TABLERO_DIM - 1 - r) * 0.5 # Bonificación por avance (más cerca de coronarse)
            elif pieza == DAMA_BLANCA:
                score_blanco += 50 # Valor más alto para dama blanca
            elif pieza == JUGADOR_NEGRO:
                score_negro += 10  # Valor base para peón negro
                score_negro += r * 0.5 # Bonificación por avance
            elif pieza == DAMA_NEGRA:
                score_negro += 50 # Valor más alto para dama negra
    
    return score_blanco - score_negro

def algoritmo_minimax(tablero, jugador_actual):
    """
    Implementación del algoritmo Minimax sin poda Alfa-Beta.
    Busca el mejor movimiento para el jugador_actual.
    Se incluye un límite de profundidad para manejar la complejidad de Damas.
    """
    if es_final(tablero, jugador_actual):
        return None

    PROFUNDIDAD_MAXIMA = 3 # Ajusta esta profundidad según el rendimiento deseado

    def max_valor(estado, profundidad, jugador_turno_actual_en_recursión):
        if es_final(estado, jugador_turno_actual_en_recursión) or profundidad == 0:
            return calcular_utilidad(estado, jugador_turno_actual_en_recursión), None
        
        mejor_valor = -math.inf
        mejor_movimiento = None
        
        # Los movimientos disponibles se calculan para el jugador_turno_actual_en_recursión
        for movimiento in movimientos_disponibles(estado, jugador_turno_actual_en_recursión):
            # En la recursión, el siguiente turno es del oponente
            valor, _ = min_valor(aplicar_movimiento(estado, movimiento), profundidad - 1, obtener_jugador_oponente(jugador_turno_actual_en_recursión))
            if valor > mejor_valor:
                mejor_valor = valor
                mejor_movimiento = movimiento
        return mejor_valor, mejor_movimiento

    def min_valor(estado, profundidad, jugador_turno_actual_en_recursión):
        if es_final(estado, jugador_turno_actual_en_recursión) or profundidad == 0:
            return calcular_utilidad(estado, jugador_turno_actual_en_recursión), None
        
        mejor_valor = math.inf
        mejor_movimiento = None
        
        # Los movimientos disponibles se calculan para el jugador_turno_actual_en_recursión
        for movimiento in movimientos_disponibles(estado, jugador_turno_actual_en_recursión):
            valor, _ = max_valor(aplicar_movimiento(estado, movimiento), profundidad - 1, obtener_jugador_oponente(jugador_turno_actual_en_recursión))
            if valor < mejor_valor:
                mejor_valor = valor
                mejor_movimiento = movimiento
        return mejor_valor, mejor_movimiento

    if jugador_actual == JUGADOR_BLANCO: # El jugador BLANCO (IA si juega con Blancas) intenta maximizar
        _, mejor_movimiento = max_valor(tablero, PROFUNDIDAD_MAXIMA, JUGADOR_BLANCO)
    else: # El jugador NEGRO (IA si juega con Negras) intenta minimizar
        _, mejor_movimiento = min_valor(tablero, PROFUNDIDAD_MAXIMA, JUGADOR_NEGRO)
        
    return mejor_movimiento

def algoritmo_minimax_alfa_beta(tablero, jugador_actual):
    """
    Implementación del algoritmo Minimax con Poda Alfa-Beta.
    Busca el mejor movimiento para el jugador_actual, optimizando la búsqueda.
    Se incluye un límite de profundidad para manejar la complejidad de Damas.
    """
    if es_final(tablero, jugador_actual):
        return None

    PROFUNDIDAD_MAXIMA = 5 # Generalmente se puede usar una profundidad mayor con Alfa-Beta

    def max_valor(estado, alfa, beta, profundidad, jugador_turno_actual_en_recursión):
        if es_final(estado, jugador_turno_actual_en_recursión) or profundidad == 0:
            return calcular_utilidad(estado, jugador_turno_actual_en_recursión), None
        
        mejor_valor = -math.inf
        mejor_movimiento = None
        
        for movimiento in movimientos_disponibles(estado, jugador_turno_actual_en_recursión):
            valor, _ = min_valor(aplicar_movimiento(estado, movimiento), alfa, beta, profundidad - 1, obtener_jugador_oponente(jugador_turno_actual_en_recursión))
            
            if valor > mejor_valor:
                mejor_valor = valor
                mejor_movimiento = movimiento
            
            alfa = max(alfa, mejor_valor)
            if beta <= alfa: # Poda Beta
                break
        return mejor_valor, mejor_movimiento

    def min_valor(estado, alfa, beta, profundidad, jugador_turno_actual_en_recursión):
        if es_final(estado, jugador_turno_actual_en_recursión) or profundidad == 0:
            return calcular_utilidad(estado, jugador_turno_actual_en_recursión), None
        
        mejor_valor = math.inf
        mejor_movimiento = None
        
        for movimiento in movimientos_disponibles(estado, jugador_turno_actual_en_recursión):
            valor, _ = max_valor(aplicar_movimiento(estado, movimiento), alfa, beta, profundidad - 1, obtener_jugador_oponente(jugador_turno_actual_en_recursión))
            
            if valor < mejor_valor:
                mejor_valor = valor
                mejor_movimiento = movimiento
            
            beta = min(beta, mejor_valor)
            if beta <= alfa: # Poda Alfa
                break
        return mejor_valor, mejor_movimiento

    if jugador_actual == JUGADOR_BLANCO:
        _, mejor_movimiento = max_valor(tablero, -math.inf, math.inf, PROFUNDIDAD_MAXIMA, JUGADOR_BLANCO)
    else: # Jugador NEGRO
        _, mejor_movimiento = min_valor(tablero, -math.inf, math.inf, PROFUNDIDAD_MAXIMA, JUGADOR_NEGRO)
        
    return mejor_movimiento
# busqueda.py
import math
import copy
import random

# --- Configuración del Juego de Damas ---
TABLERO_DIM = 8 # Puedes cambiar esto (8 para estándar, 10 para internacional)

JUGADOR_BLANCO = "B"  # Representa las piezas blancas
JUGADOR_NEGRO = "N"  # Representa las piezas negras
CELDA_VACIA = None    # Representa una celda vacía

# Se usará para identificar la "dama" o "reina"
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
        "nombre": "Fácil", 
        "profundidad": 2,
        "error_probabilidad": 0.2,  # 20% de probabilidad de error
        "descripcion": "IA básica, algunos errores ocasionales"
    },
    3: {
        "nombre": "Intermedio",
        "profundidad": 3,
        "error_probabilidad": 0.1,  # 10% de probabilidad de error
        "descripcion": "IA competente, pocos errores"
    },
    4: {
        "nombre": "Difícil",
        "profundidad": 4,
        "error_probabilidad": 0.05,  # 5% de probabilidad de error
        "descripcion": "IA avanzada, muy pocos errores"
    },
    5: {
        "nombre": "Experto",
        "profundidad": 5,
        "error_probabilidad": 0.0,  # Sin errores intencionales
        "descripcion": "IA máxima, juego perfecto"
    }
}

# Variable global para el nivel actual
nivel_ia_actual = 3  # Nivel intermedio por defecto

def establecer_nivel_ia(nivel):
    """
    Establece el nivel de dificultad de la IA.
    """
    global nivel_ia_actual
    if nivel in NIVELES_DIFICULTAD:
        nivel_ia_actual = nivel
        return True
    return False

def obtener_nivel_actual():
    """
    Retorna la información del nivel actual de la IA.
    """
    return NIVELES_DIFICULTAD[nivel_ia_actual]

def debe_cometer_error():
    """
    Determina si la IA debe cometer un error intencional según su nivel.
    """
    probabilidad_error = NIVELES_DIFICULTAD[nivel_ia_actual]["error_probabilidad"]
    return random.random() < probabilidad_error

def tablero_inicial():
    """
    Inicializa un tablero de Damas con la disposición estándar.
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
    En Damas tradicionales, las capturas son obligatorias cuando están disponibles.
    """
    todos_los_movimientos = set()
    movimientos_captura = set()

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
                # Obtener movimientos de captura
                saltos = _obtener_saltos_posibles(tablero, (r, c), jugador_actual, es_dama)
                movimientos_captura.update(saltos)
                
                # Solo añadir movimientos normales si no hay capturas disponibles
                if not es_dama: # Peón
                    movimientos_normales = _obtener_movimientos_normales_peon(tablero, (r, c), jugador_actual)
                else: # Dama
                    movimientos_normales = _obtener_movimientos_normales_dama(tablero, (r, c))
                
                todos_los_movimientos.update(movimientos_normales)
    
    # Si hay capturas disponibles, solo devolver las capturas (regla obligatoria)
    if movimientos_captura:
        return movimientos_captura
    else:
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
    En Damas tradicionales, se capturan piezas enemigas saltando sobre ellas.
    Las damas pueden saltar en cualquier dirección y hacer capturas múltiples.
    """
    if es_dama:
        return _obtener_saltos_dama(tablero, origen, jugador)
    else:
        return _obtener_saltos_peon(tablero, origen, jugador)

def _obtener_saltos_peon(tablero, origen, jugador):
    """
    Saltos para peones: solo hacia adelante, capturando piezas enemigas.
    Incluye capturas múltiples (dobles, triples, etc.)
    """
    saltos = set()
    r, c = origen
    
    # Direcciones según el jugador
    if jugador == JUGADOR_BLANCO:
        direcciones = [(-1, -1), (-1, 1)]  # Hacia arriba
    else:
        direcciones = [(1, -1), (1, 1)]   # Hacia abajo

    # Buscar capturas simples primero
    for dr, dc in direcciones:
        salto_r, salto_c = r + dr, c + dc
        destino_r, destino_c = r + 2 * dr, c + 2 * dc

        if (0 <= salto_r < TABLERO_DIM and 0 <= salto_c < TABLERO_DIM and
            0 <= destino_r < TABLERO_DIM and 0 <= destino_c < TABLERO_DIM):
            
            pieza_saltada = tablero[salto_r][salto_c]
            
            if (_es_pieza_enemiga(pieza_saltada, jugador) and 
                tablero[destino_r][destino_c] == CELDA_VACIA and
                (destino_r + destino_c) % 2 != 0):
                
                # Agregar captura simple
                saltos.add((origen, (destino_r, destino_c)))
                
    return saltos


def _obtener_saltos_dama(tablero, origen, jugador):
    """
    Saltos para damas: pueden saltar en cualquier dirección diagonal,
    cualquier distancia, capturando piezas enemigas.
    """
    saltos = set()
    r, c = origen
    direcciones = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

    for dr, dc in direcciones:
        for distancia in range(1, TABLERO_DIM):
            salto_r, salto_c = r + dr * distancia, c + dc * distancia
            
            if not (0 <= salto_r < TABLERO_DIM and 0 <= salto_c < TABLERO_DIM):
                break
                
            pieza_saltada = tablero[salto_r][salto_c]
            
            if pieza_saltada == CELDA_VACIA:
                continue
            elif _es_pieza_enemiga(pieza_saltada, jugador):
                # Buscar casillas vacías después de la pieza enemiga
                for destino_dist in range(distancia + 1, TABLERO_DIM):
                    destino_r, destino_c = r + dr * destino_dist, c + dc * destino_dist
                    
                    if not (0 <= destino_r < TABLERO_DIM and 0 <= destino_c < TABLERO_DIM):
                        break
                        
                    if tablero[destino_r][destino_c] == CELDA_VACIA:
                        if (destino_r + destino_c) % 2 != 0:
                            saltos.add((origen, (destino_r, destino_c)))
                    else:
                        break
                break
            else:
                break

    return saltos

def _es_pieza_enemiga(pieza, jugador):
    """
    Verifica si una pieza pertenece al jugador enemigo.
    """
    if jugador == JUGADOR_BLANCO:
        return pieza in [JUGADOR_NEGRO, DAMA_NEGRA]
    else:
        return pieza in [JUGADOR_BLANCO, DAMA_BLANCA]


def aplicar_movimiento(tablero, movimiento):
    """
    Aplica un movimiento (origen, destino) al tablero y devuelve un nuevo tablero.
    En Damas tradicionales, las piezas enemigas se capturan al ser saltadas.
    Maneja capturas múltiples eliminando todas las piezas enemigas en el camino.
    """
    nuevo_tablero = copy.deepcopy(tablero)
    (origen_r, origen_c), (destino_r, destino_c) = movimiento

    pieza_movida = nuevo_tablero[origen_r][origen_c]
    jugador_actual = JUGADOR_BLANCO if pieza_movida in [JUGADOR_BLANCO, DAMA_BLANCA] else JUGADOR_NEGRO
    
    # Detectar si es un salto (captura)
    diff_r = abs(origen_r - destino_r)
    diff_c = abs(origen_c - destino_c)
    
    if diff_r > 1 or diff_c > 1:  # Es un salto/captura
        # Para capturas múltiples, necesitamos simular el camino completo
        piezas_capturadas = _encontrar_todas_las_piezas_capturadas(tablero, (origen_r, origen_c), (destino_r, destino_c), jugador_actual)
        
        # Eliminar todas las piezas capturadas
        for cap_r, cap_c in piezas_capturadas:
            nuevo_tablero[cap_r][cap_c] = CELDA_VACIA
    
    # Mover la pieza al destino final
    nuevo_tablero[destino_r][destino_c] = pieza_movida
    nuevo_tablero[origen_r][origen_c] = CELDA_VACIA

    # Lógica de coronación (promoción a Dama)
    if pieza_movida == JUGADOR_BLANCO and destino_r == 0: # Blanco llega a la primera fila
        nuevo_tablero[destino_r][destino_c] = DAMA_BLANCA
    elif pieza_movida == JUGADOR_NEGRO and destino_r == TABLERO_DIM - 1: # Negro llega a la última fila
        nuevo_tablero[destino_r][destino_c] = DAMA_NEGRA

    return nuevo_tablero

def _encontrar_todas_las_piezas_capturadas(tablero, origen, destino, jugador):
    """
    Encuentra TODAS las piezas enemigas que deben ser capturadas en un movimiento.
    Método simplificado: recorre todo el camino desde origen hasta destino
    y encuentra todas las piezas enemigas en el camino.
    """
    origen_r, origen_c = origen
    destino_r, destino_c = destino
    piezas_capturadas = []
    
    # Calcular la dirección del movimiento
    dr = 0 if destino_r == origen_r else (1 if destino_r > origen_r else -1)
    dc = 0 if destino_c == origen_c else (1 if destino_c > origen_c else -1)
    
    # Recorrer todo el camino desde origen hasta destino
    r, c = origen_r + dr, origen_c + dc
    
    while r != destino_r or c != destino_c:
        # Verificar límites del tablero
        if not (0 <= r < TABLERO_DIM and 0 <= c < TABLERO_DIM):
            break
            
        # Si hay una pieza en esta posición y es enemiga, capturarla
        if tablero[r][c] != CELDA_VACIA and _es_pieza_enemiga(tablero[r][c], jugador):
            piezas_capturadas.append((r, c))
        
        # Avanzar en la dirección del movimiento
        r += dr
        c += dc
    
    return piezas_capturadas

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
                score_blanco += (TABLERO_DIM - 1 - r) * 1.0 # Bonificación por avance (más cerca de coronarse)
            elif pieza == DAMA_BLANCA:
                score_blanco += 80 # Valor mucho más alto para dama blanca
                # Bonificar damas en el centro del tablero (más movilidad)
                centro_dist = abs(r - TABLERO_DIM//2) + abs(c - TABLERO_DIM//2)
                score_blanco += (TABLERO_DIM - centro_dist) * 2
            elif pieza == JUGADOR_NEGRO:
                score_negro += 10  # Valor base para peón negro
                score_negro += r * 1.0 # Bonificación por avance
            elif pieza == DAMA_NEGRA:
                score_negro += 80 # Valor mucho más alto para dama negra
                # Bonificar damas en el centro del tablero (más movilidad)
                centro_dist = abs(r - TABLERO_DIM//2) + abs(c - TABLERO_DIM//2)
                score_negro += (TABLERO_DIM - centro_dist) * 2
    
    # Simplificar el cálculo de movilidad para evitar recursión excesiva
    try:
        movimientos_blanco = len(movimientos_disponibles(tablero, JUGADOR_BLANCO))
        movimientos_negro = len(movimientos_disponibles(tablero, JUGADOR_NEGRO))
        
        score_blanco += movimientos_blanco * 0.5
        score_negro += movimientos_negro * 0.5
    except:
        # Si hay error en el cálculo de movimientos, usar solo el score de piezas
        pass
    
    return score_blanco - score_negro

def _es_captura(tablero, movimiento):
    """
    Verifica si un movimiento es una captura.
    """
    (origen_r, origen_c), (destino_r, destino_c) = movimiento
    diff_r = abs(origen_r - destino_r)
    diff_c = abs(origen_c - destino_c)
    return diff_r > 1 or diff_c > 1

def algoritmo_minimax(tablero, jugador_actual):
    """
    Implementación del algoritmo Minimax sin poda Alfa-Beta.
    Busca el mejor movimiento para el jugador_actual.
    La profundidad se ajusta según el nivel de dificultad actual.
    """
    if es_final(tablero, jugador_actual):
        return None

    PROFUNDIDAD_MAXIMA = NIVELES_DIFICULTAD[nivel_ia_actual]["profundidad"]

    def max_valor(estado, profundidad, jugador_turno_actual_en_recursión):
        if es_final(estado, jugador_turno_actual_en_recursión) or profundidad == 0:
            return calcular_utilidad(estado, jugador_turno_actual_en_recursión), None
        
        mejor_valor = -math.inf
        mejor_movimiento = None
        
        for movimiento in movimientos_disponibles(estado, jugador_turno_actual_en_recursión):
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
        
        for movimiento in movimientos_disponibles(estado, jugador_turno_actual_en_recursión):
            valor, _ = max_valor(aplicar_movimiento(estado, movimiento), profundidad - 1, obtener_jugador_oponente(jugador_turno_actual_en_recursión))
            if valor < mejor_valor:
                mejor_valor = valor
                mejor_movimiento = movimiento
        return mejor_valor, mejor_movimiento

    if jugador_actual == JUGADOR_BLANCO:
        _, mejor_movimiento = max_valor(tablero, PROFUNDIDAD_MAXIMA, JUGADOR_BLANCO)
    else:
        _, mejor_movimiento = min_valor(tablero, PROFUNDIDAD_MAXIMA, JUGADOR_NEGRO)
    
    # Aplicar errores ocasionales según el nivel
    if debe_cometer_error() and mejor_movimiento:
        movimientos_disponibles_lista = list(movimientos_disponibles(tablero, jugador_actual))
        if len(movimientos_disponibles_lista) > 1:
            # Elegir un movimiento aleatorio en lugar del mejor
            movimientos_disponibles_lista.remove(mejor_movimiento)
            mejor_movimiento = random.choice(movimientos_disponibles_lista)
        
    return mejor_movimiento

def algoritmo_minimax_alfa_beta(tablero, jugador_actual):
    """
    Implementación del algoritmo Minimax con Poda Alfa-Beta.
    Busca el mejor movimiento para el jugador_actual, optimizando la búsqueda.
    La profundidad se ajusta según el nivel de dificultad actual.
    """
    if es_final(tablero, jugador_actual):
        return None

    PROFUNDIDAD_MAXIMA = NIVELES_DIFICULTAD[nivel_ia_actual]["profundidad"]

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
            if beta <= alfa:
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
            if beta <= alfa:
                break
        return mejor_valor, mejor_movimiento

    if jugador_actual == JUGADOR_BLANCO:
        _, mejor_movimiento = max_valor(tablero, -math.inf, math.inf, PROFUNDIDAD_MAXIMA, JUGADOR_BLANCO)
    else:
        _, mejor_movimiento = min_valor(tablero, -math.inf, math.inf, PROFUNDIDAD_MAXIMA, JUGADOR_NEGRO)
    
    # Aplicar errores ocasionales según el nivel
    if debe_cometer_error() and mejor_movimiento:
        movimientos_disponibles_lista = list(movimientos_disponibles(tablero, jugador_actual))
        if len(movimientos_disponibles_lista) > 1:
            # Elegir un movimiento aleatorio en lugar del mejor
            movimientos_disponibles_lista.remove(mejor_movimiento)
            mejor_movimiento = random.choice(movimientos_disponibles_lista)
        
    return mejor_movimiento
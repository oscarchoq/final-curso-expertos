# tablero.py
"""
Clase Tablero para manejar el estado del juego y las reglas de damas.
"""
import copy
from configuracion import *


class Tablero:
    """
    Representa el tablero de damas y maneja todas las operaciones relacionadas
    con el estado del juego, movimientos válidos y reglas.
    """
    
    def __init__(self):
        """Inicializa un tablero vacío."""
        self.tablero = [[CELDA_VACIA for _ in range(TABLERO_DIM)] for _ in range(TABLERO_DIM)]
        self.inicializar_tablero()
    
    def inicializar_tablero(self):
        """
        Inicializa el tablero con la disposición estándar de damas.
        Las fichas se colocan solo en las casillas oscuras.
        """
        for r in range(TABLERO_DIM):
            for c in range(TABLERO_DIM):
                if (r + c) % 2 != 0:  # Casilla oscura
                    if r < (TABLERO_DIM // 2) - 1:  # Filas para jugador negro
                        self.tablero[r][c] = JUGADOR_NEGRO
                    elif r >= (TABLERO_DIM // 2) + 1:  # Filas para jugador blanco
                        self.tablero[r][c] = JUGADOR_BLANCO
    
    def obtener_tablero(self):
        """Retorna una copia del estado actual del tablero."""
        return copy.deepcopy(self.tablero)
    
    def establecer_tablero(self, nuevo_tablero):
        """Establece un nuevo estado del tablero."""
        self.tablero = copy.deepcopy(nuevo_tablero)
    
    def es_casilla_valida(self, fila, columna):
        """Verifica si una posición está dentro del tablero."""
        return 0 <= fila < TABLERO_DIM and 0 <= columna < TABLERO_DIM
    
    def es_casilla_oscura(self, fila, columna):
        """Verifica si una casilla es oscura (donde se pueden colocar piezas)."""
        return (fila + columna) % 2 != 0
    
    def obtener_pieza(self, fila, columna):
        """Obtiene la pieza en una posición específica."""
        if self.es_casilla_valida(fila, columna):
            return self.tablero[fila][columna]
        return None
    
    def es_pieza_del_jugador(self, fila, columna, jugador):
        """Verifica si la pieza en una posición pertenece al jugador especificado."""
        pieza = self.obtener_pieza(fila, columna)
        if jugador == JUGADOR_BLANCO:
            return pieza in [JUGADOR_BLANCO, DAMA_BLANCA]
        elif jugador == JUGADOR_NEGRO:
            return pieza in [JUGADOR_NEGRO, DAMA_NEGRA]
        return False
    
    def es_pieza_enemiga(self, fila, columna, jugador):
        """Verifica si la pieza en una posición es enemiga del jugador."""
        pieza = self.obtener_pieza(fila, columna)
        if jugador == JUGADOR_BLANCO:
            return pieza in [JUGADOR_NEGRO, DAMA_NEGRA]
        else:
            return pieza in [JUGADOR_BLANCO, DAMA_BLANCA]
    
    def es_dama(self, fila, columna):
        """Verifica si la pieza en una posición es una dama."""
        pieza = self.obtener_pieza(fila, columna)
        return pieza in [DAMA_BLANCA, DAMA_NEGRA]
    
    def movimientos_disponibles(self, jugador):
        """
        Retorna todos los movimientos válidos para un jugador.
        Las capturas son obligatorias cuando están disponibles.
        """
        movimientos_captura = set()
        movimientos_normales = set()
        
        for fila in range(TABLERO_DIM):
            for columna in range(TABLERO_DIM):
                if self.es_pieza_del_jugador(fila, columna, jugador):
                    es_dama = self.es_dama(fila, columna)
                    
                    # Obtener capturas
                    capturas = self._obtener_capturas(fila, columna, jugador, es_dama)
                    movimientos_captura.update(capturas)
                    
                    # Obtener movimientos normales
                    if es_dama:
                        normales = self._obtener_movimientos_dama(fila, columna)
                    else:
                        normales = self._obtener_movimientos_peon(fila, columna, jugador)
                    movimientos_normales.update(normales)
        
        # Si hay capturas disponibles, solo devolver capturas (regla obligatoria)
        return movimientos_captura if movimientos_captura else movimientos_normales
    
    def _obtener_movimientos_peon(self, fila, columna, jugador):
        """Obtiene movimientos normales para un peón."""
        movimientos = set()
        
        # Direcciones de avance según el jugador
        if jugador == JUGADOR_BLANCO:
            direcciones = [(-1, -1), (-1, 1)]  # Hacia arriba
        else:
            direcciones = [(1, -1), (1, 1)]   # Hacia abajo
        
        for df, dc in direcciones:
            nueva_fila, nueva_columna = fila + df, columna + dc
            if (self.es_casilla_valida(nueva_fila, nueva_columna) and
                self.obtener_pieza(nueva_fila, nueva_columna) == CELDA_VACIA):
                movimientos.add(((fila, columna), (nueva_fila, nueva_columna)))
        
        return movimientos
    
    def _obtener_movimientos_dama(self, fila, columna):
        """Obtiene movimientos normales para una dama."""
        movimientos = set()
        direcciones = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        for df, dc in direcciones:
            for distancia in range(1, TABLERO_DIM):
                nueva_fila = fila + df * distancia
                nueva_columna = columna + dc * distancia
                
                if not self.es_casilla_valida(nueva_fila, nueva_columna):
                    break
                
                if self.obtener_pieza(nueva_fila, nueva_columna) == CELDA_VACIA:
                    movimientos.add(((fila, columna), (nueva_fila, nueva_columna)))
                else:
                    break  # Bloqueado por otra pieza
        
        return movimientos
    
    def _obtener_capturas(self, fila, columna, jugador, es_dama):
        """Obtiene todas las capturas posibles para una pieza."""
        if es_dama:
            return self._obtener_capturas_dama(fila, columna, jugador)
        else:
            return self._obtener_capturas_peon(fila, columna, jugador)
    
    def _obtener_capturas_peon(self, fila, columna, jugador):
        """Obtiene capturas para un peón."""
        capturas = set()
        
        # Direcciones según el jugador
        if jugador == JUGADOR_BLANCO:
            direcciones = [(-1, -1), (-1, 1)]
        else:
            direcciones = [(1, -1), (1, 1)]
        
        for df, dc in direcciones:
            fila_salto = fila + df
            columna_salto = columna + dc
            fila_destino = fila + 2 * df
            columna_destino = columna + 2 * dc
            
            if (self.es_casilla_valida(fila_salto, columna_salto) and
                self.es_casilla_valida(fila_destino, columna_destino) and
                self.es_pieza_enemiga(fila_salto, columna_salto, jugador) and
                self.obtener_pieza(fila_destino, columna_destino) == CELDA_VACIA):
                capturas.add(((fila, columna), (fila_destino, columna_destino)))
        
        return capturas
    
    def _obtener_capturas_dama(self, fila, columna, jugador):
        """Obtiene capturas para una dama."""
        capturas = set()
        direcciones = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        for df, dc in direcciones:
            for distancia in range(1, TABLERO_DIM):
                fila_salto = fila + df * distancia
                columna_salto = columna + dc * distancia
                
                if not self.es_casilla_valida(fila_salto, columna_salto):
                    break
                
                pieza_saltada = self.obtener_pieza(fila_salto, columna_salto)
                
                if pieza_saltada == CELDA_VACIA:
                    continue
                elif self.es_pieza_enemiga(fila_salto, columna_salto, jugador):
                    # Buscar destinos válidos después de la captura
                    for dist_destino in range(distancia + 1, TABLERO_DIM):
                        fila_destino = fila + df * dist_destino
                        columna_destino = columna + dc * dist_destino
                        
                        if not self.es_casilla_valida(fila_destino, columna_destino):
                            break
                        
                        if (self.obtener_pieza(fila_destino, columna_destino) == CELDA_VACIA):
                            capturas.add(((fila, columna), (fila_destino, columna_destino)))
                        else:
                            break
                    break
                else:
                    break
        
        return capturas
    
    def aplicar_movimiento(self, movimiento):
        """
        Aplica un movimiento al tablero y retorna un nuevo tablero.
        Maneja capturas, capturas múltiples y coronación.
        """
        nuevo_tablero = Tablero()
        nuevo_tablero.establecer_tablero(self.tablero)
        
        (origen_f, origen_c), (destino_f, destino_c) = movimiento
        pieza_movida = nuevo_tablero.obtener_pieza(origen_f, origen_c)
        
        # Determinar el jugador actual
        if pieza_movida in [JUGADOR_BLANCO, DAMA_BLANCA]:
            jugador_actual = JUGADOR_BLANCO
        else:
            jugador_actual = JUGADOR_NEGRO
        
        # Detectar si es una captura
        diff_f = abs(origen_f - destino_f)
        diff_c = abs(origen_c - destino_c)
        
        if diff_f > 1 or diff_c > 1:  # Es una captura
            piezas_capturadas = self._encontrar_piezas_capturadas(
                origen_f, origen_c, destino_f, destino_c, jugador_actual
            )
            
            # Eliminar piezas capturadas
            for cap_f, cap_c in piezas_capturadas:
                nuevo_tablero.tablero[cap_f][cap_c] = CELDA_VACIA
        
        # Mover la pieza
        nuevo_tablero.tablero[destino_f][destino_c] = pieza_movida
        nuevo_tablero.tablero[origen_f][origen_c] = CELDA_VACIA
        
        # Coronación
        if (pieza_movida == JUGADOR_BLANCO and destino_f == 0):
            nuevo_tablero.tablero[destino_f][destino_c] = DAMA_BLANCA
        elif (pieza_movida == JUGADOR_NEGRO and destino_f == TABLERO_DIM - 1):
            nuevo_tablero.tablero[destino_f][destino_c] = DAMA_NEGRA
        
        return nuevo_tablero
    
    def _encontrar_piezas_capturadas(self, origen_f, origen_c, destino_f, destino_c, jugador):
        """Encuentra todas las piezas capturadas en un movimiento."""
        piezas_capturadas = []
        
        # Calcular dirección del movimiento
        df = 0 if destino_f == origen_f else (1 if destino_f > origen_f else -1)
        dc = 0 if destino_c == origen_c else (1 if destino_c > origen_c else -1)
        
        # Recorrer el camino desde origen hasta destino
        f, c = origen_f + df, origen_c + dc
        
        while f != destino_f or c != destino_c:
            if not self.es_casilla_valida(f, c):
                break
            
            if (self.obtener_pieza(f, c) != CELDA_VACIA and
                self.es_pieza_enemiga(f, c, jugador)):
                piezas_capturadas.append((f, c))
            
            f += df
            c += dc
        
        return piezas_capturadas
    
    def determinar_ganador(self, jugador_actual):
        """Determina si hay un ganador en el juego."""
        # Contar piezas
        piezas_blancas = 0
        piezas_negras = 0
        
        for fila in range(TABLERO_DIM):
            for columna in range(TABLERO_DIM):
                pieza = self.obtener_pieza(fila, columna)
                if pieza in [JUGADOR_BLANCO, DAMA_BLANCA]:
                    piezas_blancas += 1
                elif pieza in [JUGADOR_NEGRO, DAMA_NEGRA]:
                    piezas_negras += 1
        
        # Verificar si un jugador no tiene piezas
        if piezas_blancas == 0:
            return JUGADOR_NEGRO
        if piezas_negras == 0:
            return JUGADOR_BLANCO
        
        # Verificar si el jugador actual no tiene movimientos
        if not self.movimientos_disponibles(jugador_actual):
            return JUGADOR_NEGRO if jugador_actual == JUGADOR_BLANCO else JUGADOR_BLANCO
        
        return None  # No hay ganador
    
    def es_final(self, jugador_actual):
        """Verifica si el juego ha terminado."""
        return self.determinar_ganador(jugador_actual) is not None
    
    def obtener_jugador_oponente(self, jugador):
        """Retorna el jugador opuesto."""
        return JUGADOR_NEGRO if jugador == JUGADOR_BLANCO else JUGADOR_BLANCO

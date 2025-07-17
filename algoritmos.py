# algoritmos_ia.py
"""
Algoritmos de inteligencia artificial para el juego de damas.
Incluye algoritmos de búsqueda Minimax y Minimax con poda Alfa-Beta.
"""
import math
import random
from configuracion import *
from tablero import Tablero
from jugador import Jugador


class ConfiguracionIA:
    """Maneja la configuración de la IA."""
    
    def __init__(self, nivel=3):
        self.nivel_actual = nivel
    
    def establecer_nivel(self, nivel):
        """Establece el nivel de dificultad de la IA."""
        if nivel in NIVELES_DIFICULTAD:
            self.nivel_actual = nivel
            return True
        return False
    
    def obtener_nivel_actual(self):
        """Retorna la información del nivel actual."""
        return NIVELES_DIFICULTAD[self.nivel_actual]
    
    def obtener_profundidad(self):
        """Retorna la profundidad de búsqueda para el nivel actual."""
        return NIVELES_DIFICULTAD[self.nivel_actual]["profundidad"]
    
    def debe_cometer_error(self):
        """Determina si la IA debe cometer un error intencional."""
        probabilidad_error = NIVELES_DIFICULTAD[self.nivel_actual]["error_probabilidad"]
        return random.random() < probabilidad_error


class EvaluadorTablero:
    """Evalúa la utilidad de un estado del tablero."""
    
    @staticmethod
    def calcular_utilidad(tablero, jugador_para_evaluar):
        """
        Calcula la utilidad heurística del tablero.
        Valor positivo significa ventaja para BLANCO, negativo para NEGRO.
        """
        ganador = tablero.determinar_ganador(jugador_para_evaluar)
        if ganador == JUGADOR_BLANCO:
            return VALOR_GANADOR
        elif ganador == JUGADOR_NEGRO:
            return -VALOR_GANADOR
        
        score_blanco = 0
        score_negro = 0
        
        # Evaluar piezas y posiciones
        for fila in range(TABLERO_DIM):
            for columna in range(TABLERO_DIM):
                pieza = tablero.obtener_pieza(fila, columna)
                
                if pieza == JUGADOR_BLANCO:
                    score_blanco += VALOR_PEON
                    # Bonificación por avance (cercanía a coronarse)
                    score_blanco += (TABLERO_DIM - 1 - fila) * VALOR_AVANCE
                    
                elif pieza == DAMA_BLANCA:
                    score_blanco += VALOR_DAMA
                    # Bonificación por posición central (más movilidad)
                    centro_dist = abs(fila - TABLERO_DIM//2) + abs(columna - TABLERO_DIM//2)
                    score_blanco += (TABLERO_DIM - centro_dist) * VALOR_CENTRO
                    
                elif pieza == JUGADOR_NEGRO:
                    score_negro += VALOR_PEON
                    # Bonificación por avance
                    score_negro += fila * VALOR_AVANCE
                    
                elif pieza == DAMA_NEGRA:
                    score_negro += VALOR_DAMA
                    # Bonificación por posición central
                    centro_dist = abs(fila - TABLERO_DIM//2) + abs(columna - TABLERO_DIM//2)
                    score_negro += (TABLERO_DIM - centro_dist) * VALOR_CENTRO
        
        # Evaluar movilidad (cantidad de movimientos disponibles)
        try:
            movimientos_blanco = len(tablero.movimientos_disponibles(JUGADOR_BLANCO))
            movimientos_negro = len(tablero.movimientos_disponibles(JUGADOR_NEGRO))
            
            score_blanco += movimientos_blanco * VALOR_MOVILIDAD
            score_negro += movimientos_negro * VALOR_MOVILIDAD
        except (AttributeError, TypeError) as e:
            # Si hay error en el cálculo de movimientos, usar solo el score de piezas
            print(f"Advertencia: Error calculando movilidad: {e}")
            pass
        
        return score_blanco - score_negro


class AlgoritmoMinimax:
    """Implementa el algoritmo Minimax básico."""
    
    def __init__(self, configuracion_ia):
        self.config = configuracion_ia
        self.evaluador = EvaluadorTablero()
    
    def obtener_mejor_movimiento(self, tablero, jugador_actual):
        """
        Encuentra el mejor movimiento usando el algoritmo Minimax.
        
        Args:
            tablero: Estado actual del tablero
            jugador_actual: Jugador que debe mover
            
        Returns:
            Mejor movimiento encontrado o None si no hay movimientos
        """
        if tablero.es_final(jugador_actual):
            return None
        
        profundidad_maxima = self.config.obtener_profundidad()
        
        if jugador_actual == JUGADOR_BLANCO:
            _, mejor_movimiento = self._max_valor(tablero, profundidad_maxima, JUGADOR_BLANCO)
        else:
            _, mejor_movimiento = self._min_valor(tablero, profundidad_maxima, JUGADOR_NEGRO)
        
        # Aplicar errores ocasionales según el nivel
        if self.config.debe_cometer_error() and mejor_movimiento:
            movimientos_disponibles = list(tablero.movimientos_disponibles(jugador_actual))
            if len(movimientos_disponibles) > 1:
                movimientos_disponibles.remove(mejor_movimiento)
                mejor_movimiento = random.choice(movimientos_disponibles)
        
        return mejor_movimiento
    
    def _max_valor(self, tablero, profundidad, jugador_turno):
        """Función MAX del algoritmo Minimax."""
        if tablero.es_final(jugador_turno) or profundidad == 0:
            return self.evaluador.calcular_utilidad(tablero, jugador_turno), None
        
        mejor_valor = -math.inf
        mejor_movimiento = None
        
        for movimiento in tablero.movimientos_disponibles(jugador_turno):
            nuevo_tablero = tablero.aplicar_movimiento(movimiento)
            oponente = tablero.obtener_jugador_oponente(jugador_turno)
            valor, _ = self._min_valor(nuevo_tablero, profundidad - 1, oponente)
            
            if valor > mejor_valor:
                mejor_valor = valor
                mejor_movimiento = movimiento
        
        return mejor_valor, mejor_movimiento
    
    def _min_valor(self, tablero, profundidad, jugador_turno):
        """Función MIN del algoritmo Minimax."""
        if tablero.es_final(jugador_turno) or profundidad == 0:
            return self.evaluador.calcular_utilidad(tablero, jugador_turno), None
        
        mejor_valor = math.inf
        mejor_movimiento = None
        
        for movimiento in tablero.movimientos_disponibles(jugador_turno):
            nuevo_tablero = tablero.aplicar_movimiento(movimiento)
            oponente = tablero.obtener_jugador_oponente(jugador_turno)
            valor, _ = self._max_valor(nuevo_tablero, profundidad - 1, oponente)
            
            if valor < mejor_valor:
                mejor_valor = valor
                mejor_movimiento = movimiento
        
        return mejor_valor, mejor_movimiento


class AlgoritmoMinimaxAlfaBeta:
    """Implementa el algoritmo Minimax con poda Alfa-Beta."""
    
    def __init__(self, configuracion_ia):
        self.config = configuracion_ia
        self.evaluador = EvaluadorTablero()
    
    def obtener_mejor_movimiento(self, tablero, jugador_actual):
        """
        Encuentra el mejor movimiento usando Minimax con poda Alfa-Beta.
        
        Args:
            tablero: Estado actual del tablero
            jugador_actual: Jugador que debe mover
            
        Returns:
            Mejor movimiento encontrado o None si no hay movimientos
        """
        if tablero.es_final(jugador_actual):
            return None
        
        profundidad_maxima = self.config.obtener_profundidad()
        
        if jugador_actual == JUGADOR_BLANCO:
            _, mejor_movimiento = self._max_valor(
                tablero, -math.inf, math.inf, profundidad_maxima, JUGADOR_BLANCO
            )
        else:
            _, mejor_movimiento = self._min_valor(
                tablero, -math.inf, math.inf, profundidad_maxima, JUGADOR_NEGRO
            )
        
        # Aplicar errores ocasionales según el nivel
        if self.config.debe_cometer_error() and mejor_movimiento:
            movimientos_disponibles = list(tablero.movimientos_disponibles(jugador_actual))
            if len(movimientos_disponibles) > 1:
                movimientos_disponibles.remove(mejor_movimiento)
                mejor_movimiento = random.choice(movimientos_disponibles)
        
        return mejor_movimiento
    
    def _max_valor(self, tablero, alfa, beta, profundidad, jugador_turno):
        """Función MAX con poda Alfa-Beta."""
        if tablero.es_final(jugador_turno) or profundidad == 0:
            return self.evaluador.calcular_utilidad(tablero, jugador_turno), None
        
        mejor_valor = -math.inf
        mejor_movimiento = None
        
        for movimiento in tablero.movimientos_disponibles(jugador_turno):
            nuevo_tablero = tablero.aplicar_movimiento(movimiento)
            oponente = tablero.obtener_jugador_oponente(jugador_turno)
            valor, _ = self._min_valor(nuevo_tablero, alfa, beta, profundidad - 1, oponente)
            
            if valor > mejor_valor:
                mejor_valor = valor
                mejor_movimiento = movimiento
            
            alfa = max(alfa, mejor_valor)
            if beta <= alfa:
                break  # Poda Beta
        
        return mejor_valor, mejor_movimiento
    
    def _min_valor(self, tablero, alfa, beta, profundidad, jugador_turno):
        """Función MIN con poda Alfa-Beta."""
        if tablero.es_final(jugador_turno) or profundidad == 0:
            return self.evaluador.calcular_utilidad(tablero, jugador_turno), None
        
        mejor_valor = math.inf
        mejor_movimiento = None
        
        for movimiento in tablero.movimientos_disponibles(jugador_turno):
            nuevo_tablero = tablero.aplicar_movimiento(movimiento)
            oponente = tablero.obtener_jugador_oponente(jugador_turno)
            valor, _ = self._max_valor(nuevo_tablero, alfa, beta, profundidad - 1, oponente)
            
            if valor < mejor_valor:
                mejor_valor = valor
                mejor_movimiento = movimiento
            
            beta = min(beta, mejor_valor)
            if beta <= alfa:
                break  # Poda Alfa
        
        return mejor_valor, mejor_movimiento


class JugadorIA(Jugador):
    """Jugador controlado por inteligencia artificial."""
    
    def __init__(self, color, nivel=3, usar_alfa_beta=True):
        super().__init__(color)
        self.config = ConfiguracionIA(nivel)
        self.usar_alfa_beta = usar_alfa_beta
        
        if usar_alfa_beta:
            self.algoritmo = AlgoritmoMinimaxAlfaBeta(self.config)
        else:
            self.algoritmo = AlgoritmoMinimax(self.config)
    
    def establecer_nivel(self, nivel):
        """Establece el nivel de dificultad de la IA."""
        return self.config.establecer_nivel(nivel)
    
    def obtener_nivel_actual(self):
        """Obtiene la información del nivel actual."""
        return self.config.obtener_nivel_actual()
    
    def obtener_movimiento(self, tablero):
        """
        Calcula y retorna el mejor movimiento según la IA.
        
        Args:
            tablero: Estado actual del tablero
            
        Returns:
            Mejor movimiento calculado por la IA
        """
        return self.algoritmo.obtener_mejor_movimiento(tablero, self.color)
    
    def cambiar_algoritmo(self, usar_alfa_beta=True):
        """Cambia entre algoritmo Minimax básico y con poda Alfa-Beta."""
        self.usar_alfa_beta = usar_alfa_beta
        if usar_alfa_beta:
            self.algoritmo = AlgoritmoMinimaxAlfaBeta(self.config)
        else:
            self.algoritmo = AlgoritmoMinimax(self.config)

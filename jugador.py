# jugador.py
"""
Clases para manejar los movimientos y estrategias de los jugadores.
"""
import random
from configuracion import *
from tablero import Tablero


class Jugador:
    """Clase base para representar un jugador."""
    
    def __init__(self, color):
        """
        Inicializa un jugador.
        
        Args:
            color: JUGADOR_BLANCO o JUGADOR_NEGRO
        """
        self.color = color
        self.nombre = "Blancas" if color == JUGADOR_BLANCO else "Negras"
    
    def obtener_movimiento(self, tablero):
        """
        Método abstracto para obtener el próximo movimiento.
        Debe ser implementado por las subclases.
        """
        raise NotImplementedError("Debe implementarse en la subclase")


class JugadorHumano(Jugador):
    """Representa un jugador humano."""
    
    def __init__(self, color, gestor_movimientos=None, controlador_captura=None):
        super().__init__(color)
        self.gestor_movimientos = gestor_movimientos or GestorMovimientos()
        self.controlador_captura = controlador_captura or ControladorCapturaMultiple()
        self.movimiento_seleccionado = None
        self.esperando_movimiento = False
    
    def obtener_movimiento(self, tablero):
        """
        Retorna el movimiento seleccionado por el jugador humano.
        Este método es llamado por la interfaz gráfica.
        """
        if self.movimiento_seleccionado:
            movimiento = self.movimiento_seleccionado
            self.movimiento_seleccionado = None
            self.esperando_movimiento = False
            return movimiento
        
        self.esperando_movimiento = True
        return None
    
    def establecer_movimiento(self, movimiento):
        """Establece el movimiento seleccionado por el jugador."""
        self.movimiento_seleccionado = movimiento
    
    def esta_esperando_movimiento(self):
        """Verifica si el jugador está esperando que se haga un movimiento."""
        return self.esperando_movimiento
    
    def obtener_movimientos_validos(self, tablero):
        """Obtiene todos los movimientos válidos para el jugador."""
        return tablero.movimientos_disponibles(self.color)
    
    def validar_movimiento(self, tablero, origen, destino):
        """
        Valida si un movimiento es legal.
        
        Args:
            tablero: Instancia del tablero actual
            origen: Tupla (fila, columna) de origen
            destino: Tupla (fila, columna) de destino
            
        Returns:
            bool: True si el movimiento es válido
        """
        movimientos_validos = self.obtener_movimientos_validos(tablero)
        return (origen, destino) in movimientos_validos
    
    def puede_continuar_capturando(self, tablero, posicion):
        """
        Verifica si el jugador puede continuar capturando desde una posición.
        Usado para capturas múltiples obligatorias.
        """
        fila, columna = posicion
        if not tablero.es_pieza_del_jugador(fila, columna, self.color):
            return False
        
        es_dama = tablero.es_dama(fila, columna)
        capturas = tablero._obtener_capturas(fila, columna, self.color, es_dama)
        return len(capturas) > 0


class ControladorCapturaMultiple:
    """
    Maneja la lógica de capturas múltiples obligatorias.
    """
    
    def __init__(self):
        self.en_captura_multiple = False
        self.posicion_actual = None
        self.ultimo_movimiento_fue_captura = False
    
    def iniciar_captura_multiple(self, posicion_destino):
        """Inicia una secuencia de captura múltiple."""
        self.en_captura_multiple = True
        self.posicion_actual = posicion_destino
        self.ultimo_movimiento_fue_captura = True
    
    def finalizar_captura_multiple(self):
        """Finaliza una secuencia de captura múltiple."""
        self.en_captura_multiple = False
        self.posicion_actual = None
        self.ultimo_movimiento_fue_captura = False
    
    def debe_continuar_capturando(self, tablero, jugador):
        """
        Verifica si el jugador debe continuar capturando.
        
        Returns:
            bool: True si debe continuar capturando
        """
        if not self.en_captura_multiple or not self.posicion_actual:
            return False
        
        fila, columna = self.posicion_actual
        if not tablero.es_pieza_del_jugador(fila, columna, jugador.color):
            return False
        
        es_dama = tablero.es_dama(fila, columna)
        capturas = tablero._obtener_capturas(fila, columna, jugador.color, es_dama)
        return len(capturas) > 0
    
    def obtener_capturas_disponibles(self, tablero, jugador):
        """Obtiene las capturas disponibles desde la posición actual."""
        if not self.posicion_actual:
            return set()
        
        fila, columna = self.posicion_actual
        es_dama = tablero.es_dama(fila, columna)
        return tablero._obtener_capturas(fila, columna, jugador.color, es_dama)
    
    def procesar_movimiento(self, tablero, movimiento, jugador):
        """
        Procesa un movimiento y actualiza el estado de captura múltiple.
        
        Args:
            tablero: Tablero después del movimiento
            movimiento: Tupla ((origen_f, origen_c), (destino_f, destino_c))
            jugador: Jugador que hizo el movimiento
        """
        (origen_f, origen_c), (destino_f, destino_c) = movimiento
        
        # Verificar si fue una captura
        diff_f = abs(origen_f - destino_f)
        diff_c = abs(origen_c - destino_c)
        fue_captura = diff_f > 1 or diff_c > 1
        
        if fue_captura:
            # Verificar si puede continuar capturando
            if jugador.puede_continuar_capturando(tablero, (destino_f, destino_c)):
                self.iniciar_captura_multiple((destino_f, destino_c))
            else:
                self.finalizar_captura_multiple()
        else:
            self.finalizar_captura_multiple()


class GestorMovimientos:
    """
    Gestiona los movimientos del juego incluyendo validación y capturas múltiples.
    """
    
    def __init__(self):
        self.controlador_captura = ControladorCapturaMultiple()
    
    def validar_y_ejecutar_movimiento(self, tablero, jugador, origen, destino):
        """
        Valida y ejecuta un movimiento.
        
        Args:
            tablero: Instancia del tablero actual
            jugador: Jugador que hace el movimiento
            origen: Tupla (fila, columna) de origen
            destino: Tupla (fila, columna) de destino
            
        Returns:
            tuple: (tablero_nuevo, exito, debe_continuar_capturando)
        """
        # Si estamos en captura múltiple, solo permitir capturas desde la posición actual
        if self.controlador_captura.en_captura_multiple:
            if origen != self.controlador_captura.posicion_actual:
                return tablero, False, True
            
            capturas_disponibles = self.controlador_captura.obtener_capturas_disponibles(tablero, jugador)
            if (origen, destino) not in capturas_disponibles:
                return tablero, False, True
        else:
            # Validar movimiento normal
            if not jugador.validar_movimiento(tablero, origen, destino):
                return tablero, False, False
        
        # Ejecutar el movimiento
        nuevo_tablero = tablero.aplicar_movimiento((origen, destino))
        
        # Procesar captura múltiple
        self.controlador_captura.procesar_movimiento(nuevo_tablero, (origen, destino), jugador)
        
        debe_continuar = self.controlador_captura.debe_continuar_capturando(nuevo_tablero, jugador)
        
        return nuevo_tablero, True, debe_continuar
    
    def obtener_movimientos_disponibles(self, tablero, jugador):
        """
        Obtiene los movimientos disponibles considerando capturas múltiples.
        """
        if self.controlador_captura.en_captura_multiple:
            return self.controlador_captura.obtener_capturas_disponibles(tablero, jugador)
        else:
            return jugador.obtener_movimientos_validos(tablero)
    
    def reset_captura_multiple(self):
        """Reinicia el estado de captura múltiple."""
        self.controlador_captura.finalizar_captura_multiple()
    
    def esta_en_captura_multiple(self):
        """Verifica si estamos en una secuencia de captura múltiple."""
        return self.controlador_captura.en_captura_multiple
    
    def obtener_posicion_captura(self):
        """Obtiene la posición actual en captura múltiple."""
        return self.controlador_captura.posicion_actual

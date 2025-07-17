from configuracion import *

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
    
    def __init__(self, color):
        super().__init__(color)
    
    def obtener_movimiento(self, tablero):
        return None
    
    def obtener_movimientos_validos(self, tablero):
        return tablero.movimientos_disponibles(self.color)
    
    def validar_movimiento(self, tablero, origen, destino):
        movimientos_validos = self.obtener_movimientos_validos(tablero)
        return (origen, destino) in movimientos_validos


class GestorMovimientos:
    """
    Gestiona los movimientos del juego.
    """
    
    def __init__(self):
        pass
    
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
        # Validar movimiento
        if not jugador.validar_movimiento(tablero, origen, destino):
            return tablero, False, False
        
        # Ejecutar el movimiento
        nuevo_tablero = tablero.aplicar_movimiento((origen, destino))
        
        # No hay capturas múltiples, siempre retornar False para debe_continuar
        return nuevo_tablero, True, False
    
    def obtener_movimientos_disponibles(self, tablero, jugador):
        """
        Obtiene los movimientos disponibles.
        """
        return jugador.obtener_movimientos_validos(tablero)

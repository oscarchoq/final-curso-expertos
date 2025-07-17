# juego_main.py
"""
Juego de Damas con IA - Arquitectura Orientada a Objetos Completa
Versión refactorizada sin archivos de compatibilidad
"""
import pygame
import sys
import time
import os
from typing import Optional, Tuple, Set

# Importar las clases del juego
from configuracion import *
from tablero import Tablero
from jugador import JugadorHumano, ControladorCapturaMultiple, GestorMovimientos
from algoritmos import JugadorIA


class JuegoDamas:
    """
    Clase principal que gestiona todo el juego de damas.
    Controla la interfaz gráfica, la lógica del juego y la interacción usuario-IA.
    """
    
    def __init__(self):
        """Inicializa el juego y configura Pygame."""
        pygame.init()
        
        # Configuración de ventana
        self.VENTANA_ANCHO = 800
        self.VENTANA_ALTO = 800
        self.CELDA_TAMANO = min(self.VENTANA_ANCHO, self.VENTANA_ALTO) // (TABLERO_DIM + 2)
        self.TABLERO_ORIGEN_X = (self.VENTANA_ANCHO - TABLERO_DIM * self.CELDA_TAMANO) // 2
        self.TABLERO_ORIGEN_Y = (self.VENTANA_ALTO - TABLERO_DIM * self.CELDA_TAMANO) // 2
        
        # Colores
        self.COLOR_NEGRO = (0, 0, 0)
        self.COLOR_BLANCO = (255, 255, 255)
        self.COLOR_AZUL_OSCURO = (0, 0, 139)
        self.COLOR_GRIS_CLARO = (211, 211, 211)
        self.COLOR_ROJO = (255, 0, 0)
        self.COLOR_VERDE = (0, 255, 0)
        self.COLOR_CASILLA_CLARA = (240, 217, 181)
        self.COLOR_CASILLA_OSCURA = (181, 136, 99)
        self.COLOR_RESALTADO_ULTIMO_MOVIMIENTO = (255, 215, 0)
        self.COLOR_RESALTADO_ORIGEN = (255, 165, 0)
        self.COLOR_RESALTADO_DESTINO = (255, 215, 0)
        
        # Configurar pantalla
        self.pantalla = pygame.display.set_mode((self.VENTANA_ANCHO, self.VENTANA_ALTO))
        pygame.display.set_caption("Damas IA - Arquitectura Orientada a Objetos")
        
        # Cargar fuentes
        self._cargar_fuentes()
        
        # Inicializar estado del juego
        self._inicializar_estado()
        
        # Configurar logging
        self._configurar_logging()
    
    def _cargar_fuentes(self):
        """Carga las fuentes del juego."""
        try:
            self.fuente_pequena = pygame.font.Font("OpenSans-Regular.ttf", 28)
            self.fuente_grande = pygame.font.Font("OpenSans-Regular.ttf", 40)
            self.fuente_movimiento = pygame.font.Font("OpenSans-Regular.ttf", int(self.CELDA_TAMANO * 0.6))
        except (FileNotFoundError, pygame.error) as e:
            print(f"Advertencia: No se encontró 'OpenSans-Regular.ttf' ({e}). Usando fuente por defecto.")
            self.fuente_pequena = pygame.font.Font(None, 28)
            self.fuente_grande = pygame.font.Font(None, 40)
            self.fuente_movimiento = pygame.font.Font(None, int(self.CELDA_TAMANO * 0.6))
    
    def _inicializar_estado(self):
        """Inicializa el estado del juego."""
        # Componentes principales del juego
        self.tablero = Tablero()
        self.gestor_movimientos = GestorMovimientos()
        self.controlador_captura = ControladorCapturaMultiple()
        
        # Jugadores
        self.jugador_humano: Optional[JugadorHumano] = None
        self.jugador_ia: Optional[JugadorIA] = None
        
        # Estado del juego
        self.jugador_usuario: Optional[str] = None  # Color del jugador humano
        self.jugador_activo: Optional[str] = None   # Jugador actual
        self.modo_busqueda_alfa_beta: Optional[bool] = None
        self.nivel_ia_seleccionado: Optional[int] = None
        
        # Interfaz de usuario
        self.pieza_seleccionada: Optional[Tuple[int, int]] = None
        self.movimientos_posibles: Set[Tuple[Tuple[int, int], Tuple[int, int]]] = set()
        
        # Información de movimientos
        self.ultimo_movimiento_origen: Optional[Tuple[int, int]] = None
        self.ultimo_movimiento_destino: Optional[Tuple[int, int]] = None
        self.informacion_ultimo_movimiento: str = ""
        self.ultimo_movimiento_fue_ia: bool = False
        
        # Métricas de la IA
        self.tiempo_total_ia: float = 0.0
        self.cantidad_movimientos_ia: int = 0
        self.tiempos_ia: list = []
        self.resumen_escrito: bool = False
    
    def _configurar_logging(self):
        """Configura el sistema de logging de tiempos."""
        if not os.path.exists("LogTime"):
            os.makedirs("LogTime")
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        self.nombre_archivo_log = f"LogTime/logtime_{timestamp}.txt"
        
        with open(self.nombre_archivo_log, "w", encoding="utf-8") as archivo:
            archivo.write("=== LOG DE TIEMPOS DE LA IA - JUEGO DE DAMAS ===\n")
            archivo.write(f"Inicio de sesión: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            archivo.write("="*50 + "\n\n")
    
    def configurar_jugadores(self, color_usuario: str, usar_alfa_beta: bool, nivel: int):
        """
        Configura los jugadores una vez seleccionados los parámetros.
        
        Args:
            color_usuario: Color del jugador humano (JUGADOR_BLANCO o JUGADOR_NEGRO)
            usar_alfa_beta: True para usar poda Alfa-Beta, False para Minimax básico
            nivel: Nivel de dificultad de la IA (1-5)
        """
        self.jugador_usuario = color_usuario
        self.jugador_activo = JUGADOR_BLANCO  # Siempre empiezan las blancas
        self.modo_busqueda_alfa_beta = usar_alfa_beta
        self.nivel_ia_seleccionado = nivel
        
        # Crear jugador humano
        self.jugador_humano = JugadorHumano(color_usuario, self.gestor_movimientos, self.controlador_captura)
        
        # Crear jugador IA (color opuesto al humano)
        color_ia = JUGADOR_NEGRO if color_usuario == JUGADOR_BLANCO else JUGADOR_BLANCO
        self.jugador_ia = JugadorIA(color_ia)
        self.jugador_ia.establecer_nivel(nivel)
        self.jugador_ia.cambiar_algoritmo(usar_alfa_beta=usar_alfa_beta)
    
    def reiniciar_juego(self):
        """Reinicia completamente el juego."""
        if self.cantidad_movimientos_ia > 0:
            with open(self.nombre_archivo_log, "a", encoding="utf-8") as archivo:
                archivo.write(f"\n--- NUEVA PARTIDA ---\n")
                archivo.write(f"Inicio: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        self._inicializar_estado()
    
    def obtener_informacion_movimiento(self, tablero_antes: list, tablero_despues: list, movimiento: tuple) -> str:
        """
        Analiza un movimiento y retorna información descriptiva.
        
        Args:
            tablero_antes: Estado del tablero antes del movimiento
            tablero_despues: Estado del tablero después del movimiento
            movimiento: Tupla ((origen_r, origen_c), (destino_r, destino_c))
        
        Returns:
            String con información del movimiento
        """
        origen, destino = movimiento
        pieza_movida = tablero_despues[destino[0]][destino[1]]
        
        # Verificar coronación
        se_convirtio_dama = False
        if origen[0] == 0 and pieza_movida == DAMA_NEGRA:
            se_convirtio_dama = True
        elif origen[0] == TABLERO_DIM - 1 and pieza_movida == DAMA_BLANCA:
            se_convirtio_dama = True
        
        # Contar capturas
        piezas_antes = sum(row.count(JUGADOR_BLANCO) + row.count(JUGADOR_NEGRO) + 
                          row.count(DAMA_BLANCA) + row.count(DAMA_NEGRA) for row in tablero_antes)
        piezas_despues = sum(row.count(JUGADOR_BLANCO) + row.count(JUGADOR_NEGRO) + 
                            row.count(DAMA_BLANCA) + row.count(DAMA_NEGRA) for row in tablero_despues)
        
        capturas = piezas_antes - piezas_despues
        
        info = ""
        if capturas > 0:
            if capturas == 1:
                info = "¡Captura!"
            else:
                info = f"¡Captura múltiple x{capturas}!"
        
        if se_convirtio_dama:
            if info:
                info += " ¡Nueva dama!"
            else:
                info = "¡Nueva dama!"
        
        return info
    
    def manejar_click_configuracion(self, pos_mouse: Tuple[int, int]) -> bool:
        """
        Maneja clicks en la pantalla de configuración inicial.
        
        Args:
            pos_mouse: Posición del mouse (x, y)
        
        Returns:
            True si la configuración está completa, False en caso contrario
        """
        # Dimensiones de botones
        boton_ancho = 150
        boton_alto = 45
        separacion = 60
        
        # Botones de color
        boton_blanco = pygame.Rect((self.VENTANA_ANCHO / 2 - boton_ancho - separacion/2), 210, boton_ancho, boton_alto)
        boton_negro = pygame.Rect((self.VENTANA_ANCHO / 2 + separacion/2), 210, boton_ancho, boton_alto)
        
        # Botones de algoritmo
        boton_alfa_beta = pygame.Rect((self.VENTANA_ANCHO / 2 - boton_ancho - separacion/2), 330, boton_ancho, boton_alto)
        boton_minimax = pygame.Rect((self.VENTANA_ANCHO / 2 + separacion/2), 330, boton_ancho, boton_alto)
        
        # Botones de nivel
        botones_nivel = []
        boton_nivel_tamano = 60
        espacio_entre_botones = 20
        inicio_x = self.VENTANA_ANCHO / 2 - (3 * boton_nivel_tamano + 2 * espacio_entre_botones) / 2
        
        for i in range(1, 4):
            x = inicio_x + (i - 1) * (boton_nivel_tamano + espacio_entre_botones)
            y = 450
            botones_nivel.append(pygame.Rect(x, y, boton_nivel_tamano, boton_nivel_tamano))
        
        # Procesar clicks
        if boton_blanco.collidepoint(pos_mouse):
            self.jugador_usuario = JUGADOR_BLANCO
        elif boton_negro.collidepoint(pos_mouse):
            self.jugador_usuario = JUGADOR_NEGRO
        elif boton_alfa_beta.collidepoint(pos_mouse):
            self.modo_busqueda_alfa_beta = True
        elif boton_minimax.collidepoint(pos_mouse):
            self.modo_busqueda_alfa_beta = False
        else:
            # Verificar clicks en niveles
            for i, boton in enumerate(botones_nivel):
                if boton.collidepoint(pos_mouse):
                    self.nivel_ia_seleccionado = i + 1
                    break
        
        # Verificar si la configuración está completa
        if (self.jugador_usuario is not None and 
            self.modo_busqueda_alfa_beta is not None and 
            self.nivel_ia_seleccionado is not None):
            self.configurar_jugadores(self.jugador_usuario, self.modo_busqueda_alfa_beta, self.nivel_ia_seleccionado)
            return True
        
        return False
    
    def manejar_click_juego(self, pos_mouse: Tuple[int, int]):
        """
        Maneja clicks durante el juego.
        
        Args:
            pos_mouse: Posición del mouse (x, y)
        """
        # Verificar si es turno del jugador humano
        if self.jugador_activo != self.jugador_usuario or self.tablero.es_final(self.jugador_activo):
            return
        
        # Convertir posición del mouse a coordenadas del tablero
        col = (pos_mouse[0] - self.TABLERO_ORIGEN_X) // self.CELDA_TAMANO
        row = (pos_mouse[1] - self.TABLERO_ORIGEN_Y) // self.CELDA_TAMANO
        
        # Verificar que el click esté dentro del tablero y en casilla oscura
        if not (0 <= row < TABLERO_DIM and 0 <= col < TABLERO_DIM and (row + col) % 2 != 0):
            self.pieza_seleccionada = None
            self.movimientos_posibles = set()
            return
        
        if self.pieza_seleccionada:
            # Verificar si es un movimiento válido
            movimiento_encontrado = None
            for (p_origen, p_destino) in self.movimientos_posibles:
                if p_origen == self.pieza_seleccionada and p_destino == (row, col):
                    movimiento_encontrado = (p_origen, p_destino)
                    break
            
            if movimiento_encontrado:
                self._ejecutar_movimiento_humano(movimiento_encontrado)
            else:
                self._seleccionar_pieza(row, col)
        else:
            self._seleccionar_pieza(row, col)
    
    def _seleccionar_pieza(self, row: int, col: int):
        """Selecciona una pieza del jugador actual."""
        estado_tablero = self.tablero.obtener_tablero()
        pieza_en_celda = estado_tablero[row][col]
        
        # Verificar si la pieza pertenece al jugador actual
        es_pieza_usuario = (self.jugador_usuario == JUGADOR_BLANCO and pieza_en_celda in [JUGADOR_BLANCO, DAMA_BLANCA]) or \
                          (self.jugador_usuario == JUGADOR_NEGRO and pieza_en_celda in [JUGADOR_NEGRO, DAMA_NEGRA])
        
        if es_pieza_usuario:
            self.pieza_seleccionada = (row, col)
            todos_movimientos = self.tablero.movimientos_disponibles(self.jugador_activo)
            self.movimientos_posibles = {mov for mov in todos_movimientos if mov[0] == self.pieza_seleccionada}
        else:
            self.pieza_seleccionada = None
            self.movimientos_posibles = set()
    
    def _ejecutar_movimiento_humano(self, movimiento: Tuple[Tuple[int, int], Tuple[int, int]]):
        """Ejecuta un movimiento del jugador humano."""
        estado_anterior = self.tablero.obtener_tablero()
        tablero_antes = [fila[:] for fila in estado_anterior]
        
        # Aplicar movimiento
        self.tablero = self.tablero.aplicar_movimiento(movimiento)
        estado_nuevo = self.tablero.obtener_tablero()
        
        # Actualizar información del movimiento
        self.ultimo_movimiento_origen = movimiento[0]
        self.ultimo_movimiento_destino = movimiento[1]
        self.informacion_ultimo_movimiento = self.obtener_informacion_movimiento(tablero_antes, estado_nuevo, movimiento)
        self.ultimo_movimiento_fue_ia = False
        
        # Limpiar selección y cambiar turno
        self.pieza_seleccionada = None
        self.movimientos_posibles = set()
        self.jugador_activo = JUGADOR_NEGRO if self.jugador_activo == JUGADOR_BLANCO else JUGADOR_BLANCO
    
    def ejecutar_movimiento_ia(self):
        """Ejecuta un movimiento de la IA."""
        if self.jugador_activo == self.jugador_usuario or self.tablero.es_final(self.jugador_activo):
            return
        
        # Medir tiempo de pensamiento
        tiempo_inicio = time.time()
        movimiento_ia = self.jugador_ia.obtener_movimiento(self.tablero)
        tiempo_fin = time.time()
        
        tiempo_movimiento = tiempo_fin - tiempo_inicio
        
        if movimiento_ia:
            # Guardar estado anterior
            estado_anterior = self.tablero.obtener_tablero()
            tablero_antes = [fila[:] for fila in estado_anterior]
            
            # Aplicar movimiento
            self.tablero = self.tablero.aplicar_movimiento(movimiento_ia)
            estado_nuevo = self.tablero.obtener_tablero()
            
            # Actualizar información
            self.ultimo_movimiento_origen = movimiento_ia[0]
            self.ultimo_movimiento_destino = movimiento_ia[1]
            self.informacion_ultimo_movimiento = self.obtener_informacion_movimiento(tablero_antes, estado_nuevo, movimiento_ia)
            self.ultimo_movimiento_fue_ia = True
            
            # Registrar tiempo
            self._registrar_tiempo_ia(tiempo_movimiento)
            
            # Cambiar turno
            self.jugador_activo = JUGADOR_NEGRO if self.jugador_activo == JUGADOR_BLANCO else JUGADOR_BLANCO
        else:
            print(f"La IA ({self.jugador_activo}) no encontró movimientos válidos.")
    
    def _registrar_tiempo_ia(self, tiempo: float):
        """Registra el tiempo de pensamiento de la IA."""
        self.tiempo_total_ia += tiempo
        self.cantidad_movimientos_ia += 1
        self.tiempos_ia.append(tiempo)
        
        with open(self.nombre_archivo_log, "a", encoding="utf-8") as archivo:
            if self.cantidad_movimientos_ia == 1:
                algoritmo_texto = "Alfa-Beta" if self.modo_busqueda_alfa_beta else "Minimax"
                color_ia = "Negras" if self.jugador_usuario == JUGADOR_BLANCO else "Blancas"
                archivo.write(f"Configuración: {algoritmo_texto} | Nivel {self.nivel_ia_seleccionado} | IA juega con {color_ia}\n")
                archivo.write("-" * 50 + "\n")
            
            archivo.write(f"Movimiento {self.cantidad_movimientos_ia}: {tiempo:.8f} segundos\n")
    
    def dibujar_pantalla_configuracion(self):
        """Dibuja la pantalla de configuración inicial."""
        self.pantalla.fill(self.COLOR_NEGRO)
        
        # Título
        titulo = self.fuente_grande.render("Damas IA", True, self.COLOR_AZUL_OSCURO)
        titulo_rect = titulo.get_rect(center=(self.VENTANA_ANCHO / 2, 80))
        self.pantalla.blit(titulo, titulo_rect)
        
        sub_titulo = self.fuente_pequena.render(f"Tablero {TABLERO_DIM}x{TABLERO_DIM}", True, self.COLOR_BLANCO)
        sub_titulo_rect = sub_titulo.get_rect(center=(self.VENTANA_ANCHO / 2, 120))
        self.pantalla.blit(sub_titulo, sub_titulo_rect)
        
        # Sección 1: Color
        seccion_color = self.fuente_pequena.render("1. Selecciona tu color:", True, self.COLOR_BLANCO)
        seccion_color_rect = seccion_color.get_rect(center=(self.VENTANA_ANCHO / 2, 180))
        self.pantalla.blit(seccion_color, seccion_color_rect)
        
        self._dibujar_botones_color()
        
        # Sección 2: Algoritmo
        seccion_algoritmo = self.fuente_pequena.render("2. Selecciona el algoritmo:", True, self.COLOR_BLANCO)
        seccion_algoritmo_rect = seccion_algoritmo.get_rect(center=(self.VENTANA_ANCHO / 2, 300))
        self.pantalla.blit(seccion_algoritmo, seccion_algoritmo_rect)
        
        self._dibujar_botones_algoritmo()
        
        # Sección 3: Nivel
        seccion_nivel = self.fuente_pequena.render("3. Selecciona la dificultad:", True, self.COLOR_BLANCO)
        seccion_nivel_rect = seccion_nivel.get_rect(center=(self.VENTANA_ANCHO / 2, 420))
        self.pantalla.blit(seccion_nivel, seccion_nivel_rect)
        
        self._dibujar_botones_nivel()
        
        # Mensaje de listo
        if (self.jugador_usuario is not None and 
            self.modo_busqueda_alfa_beta is not None and 
            self.nivel_ia_seleccionado is not None):
            listo_texto = self.fuente_grande.render("¡LISTO PARA JUGAR!", True, self.COLOR_VERDE)
            listo_rect = listo_texto.get_rect(center=(self.VENTANA_ANCHO / 2, 550))
            self.pantalla.blit(listo_texto, listo_rect)
    
    def _dibujar_botones_color(self):
        """Dibuja los botones de selección de color."""
        boton_ancho = 150
        boton_alto = 45
        separacion = 60
        
        # Botón blancas
        boton_blanco = pygame.Rect((self.VENTANA_ANCHO / 2 - boton_ancho - separacion/2), 210, boton_ancho, boton_alto)
        color_boton = self.COLOR_VERDE if self.jugador_usuario == JUGADOR_BLANCO else self.COLOR_GRIS_CLARO
        pygame.draw.rect(self.pantalla, color_boton, boton_blanco)
        pygame.draw.rect(self.pantalla, self.COLOR_NEGRO, boton_blanco, 2)
        
        texto_blanco = self.fuente_pequena.render("Blancas", True, self.COLOR_NEGRO)
        texto_blanco_rect = texto_blanco.get_rect(center=boton_blanco.center)
        self.pantalla.blit(texto_blanco, texto_blanco_rect)
        
        # Botón negras
        boton_negro = pygame.Rect((self.VENTANA_ANCHO / 2 + separacion/2), 210, boton_ancho, boton_alto)
        color_boton = self.COLOR_VERDE if self.jugador_usuario == JUGADOR_NEGRO else self.COLOR_GRIS_CLARO
        pygame.draw.rect(self.pantalla, color_boton, boton_negro)
        pygame.draw.rect(self.pantalla, self.COLOR_NEGRO, boton_negro, 2)
        
        texto_negro = self.fuente_pequena.render("Negras", True, self.COLOR_NEGRO)
        texto_negro_rect = texto_negro.get_rect(center=boton_negro.center)
        self.pantalla.blit(texto_negro, texto_negro_rect)
    
    def _dibujar_botones_algoritmo(self):
        """Dibuja los botones de selección de algoritmo."""
        boton_ancho = 150
        boton_alto = 45
        separacion = 60
        
        # Botón Alfa-Beta
        boton_alfa_beta = pygame.Rect((self.VENTANA_ANCHO / 2 - boton_ancho - separacion/2), 330, boton_ancho, boton_alto)
        color_boton = self.COLOR_VERDE if self.modo_busqueda_alfa_beta == True else self.COLOR_GRIS_CLARO
        pygame.draw.rect(self.pantalla, color_boton, boton_alfa_beta)
        pygame.draw.rect(self.pantalla, self.COLOR_NEGRO, boton_alfa_beta, 2)
        
        texto_alfa_beta = self.fuente_pequena.render("Alfa-Beta", True, self.COLOR_NEGRO)
        texto_alfa_beta_rect = texto_alfa_beta.get_rect(center=boton_alfa_beta.center)
        self.pantalla.blit(texto_alfa_beta, texto_alfa_beta_rect)
        
        # Botón Minimax
        boton_minimax = pygame.Rect((self.VENTANA_ANCHO / 2 + separacion/2), 330, boton_ancho, boton_alto)
        color_boton = self.COLOR_VERDE if self.modo_busqueda_alfa_beta == False else self.COLOR_GRIS_CLARO
        pygame.draw.rect(self.pantalla, color_boton, boton_minimax)
        pygame.draw.rect(self.pantalla, self.COLOR_NEGRO, boton_minimax, 2)
        
        texto_minimax = self.fuente_pequena.render("Minimax", True, self.COLOR_NEGRO)
        texto_minimax_rect = texto_minimax.get_rect(center=boton_minimax.center)
        self.pantalla.blit(texto_minimax, texto_minimax_rect)
    
    def _dibujar_botones_nivel(self):
        """Dibuja los botones de selección de nivel."""
        boton_nivel_tamano = 60
        espacio_entre_botones = 20
        inicio_x = self.VENTANA_ANCHO / 2 - (3 * boton_nivel_tamano + 2 * espacio_entre_botones) / 2
        
        for i in range(1, 4):
            x = inicio_x + (i - 1) * (boton_nivel_tamano + espacio_entre_botones)
            y = 450
            boton_nivel = pygame.Rect(x, y, boton_nivel_tamano, boton_nivel_tamano)
            
            color_boton = self.COLOR_VERDE if self.nivel_ia_seleccionado == i else self.COLOR_GRIS_CLARO
            pygame.draw.rect(self.pantalla, color_boton, boton_nivel)
            pygame.draw.rect(self.pantalla, self.COLOR_NEGRO, boton_nivel, 2)
            
            texto_nivel = self.fuente_pequena.render(str(i), True, self.COLOR_NEGRO)
            texto_nivel_rect = texto_nivel.get_rect(center=boton_nivel.center)
            self.pantalla.blit(texto_nivel, texto_nivel_rect)
    
    def dibujar_tablero(self):
        """Dibuja el tablero de juego."""
        estado_tablero = self.tablero.obtener_tablero()
        
        for r in range(TABLERO_DIM):
            for c in range(TABLERO_DIM):
                rect = pygame.Rect(
                    self.TABLERO_ORIGEN_X + c * self.CELDA_TAMANO,
                    self.TABLERO_ORIGEN_Y + r * self.CELDA_TAMANO,
                    self.CELDA_TAMANO, self.CELDA_TAMANO
                )
                
                # Color de casilla
                color_casilla = self.COLOR_CASILLA_OSCURA if (r + c) % 2 != 0 else self.COLOR_CASILLA_CLARA
                pygame.draw.rect(self.pantalla, color_casilla, rect)
                
                # Resaltar último movimiento
                if self.ultimo_movimiento_origen == (r, c):
                    pygame.draw.rect(self.pantalla, self.COLOR_RESALTADO_ORIGEN, rect, 6)
                elif self.ultimo_movimiento_destino == (r, c):
                    pygame.draw.rect(self.pantalla, self.COLOR_RESALTADO_DESTINO, rect, 6)
                
                # Resaltar pieza seleccionada
                if self.pieza_seleccionada == (r, c):
                    pygame.draw.rect(self.pantalla, self.COLOR_ROJO, rect, 4)
                
                # Mostrar movimientos posibles
                for (origen_mov, destino_mov) in self.movimientos_posibles:
                    if destino_mov == (r, c):
                        pygame.draw.circle(self.pantalla, self.COLOR_VERDE, rect.center, self.CELDA_TAMANO // 8)
                
                # Dibujar piezas
                pieza = estado_tablero[r][c]
                if pieza == JUGADOR_BLANCO:
                    pygame.draw.circle(self.pantalla, self.COLOR_BLANCO, rect.center, self.CELDA_TAMANO // 3)
                elif pieza == JUGADOR_NEGRO:
                    pygame.draw.circle(self.pantalla, self.COLOR_NEGRO, rect.center, self.CELDA_TAMANO // 3)
                elif pieza == DAMA_BLANCA:
                    pygame.draw.circle(self.pantalla, self.COLOR_BLANCO, rect.center, self.CELDA_TAMANO // 3)
                    pygame.draw.circle(self.pantalla, self.COLOR_AZUL_OSCURO, rect.center, self.CELDA_TAMANO // 4, 2)
                elif pieza == DAMA_NEGRA:
                    pygame.draw.circle(self.pantalla, self.COLOR_NEGRO, rect.center, self.CELDA_TAMANO // 3)
                    pygame.draw.circle(self.pantalla, self.COLOR_BLANCO, rect.center, self.CELDA_TAMANO // 4, 2)
    
    def dibujar_interfaz_juego(self):
        """Dibuja la interfaz durante el juego."""
        self.pantalla.fill(self.COLOR_NEGRO)
        self.dibujar_tablero()
        
        # Determinar el estado del juego
        juego_terminado = self.tablero.es_final(self.jugador_activo)
        
        if juego_terminado:
            self._dibujar_pantalla_final()
        elif self.jugador_activo == self.jugador_usuario:
            titulo = f"Tu turno: {'Blancas' if self.jugador_usuario == JUGADOR_BLANCO else 'Negras'}"
            titulo_render = self.fuente_grande.render(titulo, True, self.COLOR_BLANCO)
            titulo_rect = titulo_render.get_rect(center=(self.VENTANA_ANCHO / 2, 30))
            self.pantalla.blit(titulo_render, titulo_rect)
        else:
            titulo = "IA pensando..."
            titulo_render = self.fuente_grande.render(titulo, True, self.COLOR_BLANCO)
            titulo_rect = titulo_render.get_rect(center=(self.VENTANA_ANCHO / 2, 30))
            self.pantalla.blit(titulo_render, titulo_rect)
        
        # Información del algoritmo
        if self.modo_busqueda_alfa_beta is not None and self.nivel_ia_seleccionado is not None:
            modo_texto = "Alfa-Beta" if self.modo_busqueda_alfa_beta else "Minimax"
            info_completa = f"IA: {modo_texto} | Nivel {self.nivel_ia_seleccionado}"
            modo_info_texto = self.fuente_pequena.render(info_completa, True, self.COLOR_BLANCO)
            modo_info_rect = modo_info_texto.get_rect(center=(self.VENTANA_ANCHO / 2, self.VENTANA_ALTO - 40))
            self.pantalla.blit(modo_info_texto, modo_info_rect)
        
        # Información del último movimiento
        if self.informacion_ultimo_movimiento:
            prefijo = "IA: " if self.ultimo_movimiento_fue_ia else "Tú: "
            texto_completo = prefijo + self.informacion_ultimo_movimiento
            info_movimiento_texto = self.fuente_pequena.render(texto_completo, True, self.COLOR_RESALTADO_DESTINO)
            info_movimiento_rect = info_movimiento_texto.get_rect(center=(self.VENTANA_ANCHO / 2, self.VENTANA_ALTO - 20))
            self.pantalla.blit(info_movimiento_texto, info_movimiento_rect)
    
    def _dibujar_pantalla_final(self):
        """Dibuja la pantalla cuando el juego termina."""
        ganador = self.tablero.determinar_ganador(self.jugador_activo)
        
        if ganador is None:
            titulo_juego = "¡Empate!"
        else:
            titulo_juego = f"¡{'Blancas' if ganador == JUGADOR_BLANCO else 'Negras'} ganaron!"
        
        titulo_render = self.fuente_grande.render(titulo_juego, True, self.COLOR_BLANCO)
        titulo_rect = titulo_render.get_rect(center=(self.VENTANA_ANCHO / 2, 30))
        self.pantalla.blit(titulo_render, titulo_rect)
        
        # Estadísticas de la IA
        if self.cantidad_movimientos_ia > 0:
            tiempo_promedio = self.tiempo_total_ia / self.cantidad_movimientos_ia
            
            estadisticas_texto = f"IA realizó {self.cantidad_movimientos_ia} movimientos"
            tiempo_texto = f"Tiempo promedio: {tiempo_promedio:.8f} segundos"
            
            estadisticas_render = self.fuente_pequena.render(estadisticas_texto, True, self.COLOR_BLANCO)
            tiempo_render = self.fuente_pequena.render(tiempo_texto, True, self.COLOR_BLANCO)
            
            estadisticas_rect = estadisticas_render.get_rect(center=(self.VENTANA_ANCHO / 2, 70))
            tiempo_rect = tiempo_render.get_rect(center=(self.VENTANA_ANCHO / 2, 100))
            
            self.pantalla.blit(estadisticas_render, estadisticas_rect)
            self.pantalla.blit(tiempo_render, tiempo_rect)
            
            # Escribir resumen final
            if not self.resumen_escrito:
                self._escribir_resumen_final(titulo_juego, tiempo_promedio)
        
        # Botón para reiniciar
        boton_reiniciar = self._obtener_rect_boton_reiniciar()
        texto_reiniciar = self.fuente_pequena.render("Volver a Jugar", True, self.COLOR_NEGRO)
        texto_reiniciar_rect = texto_reiniciar.get_rect(center=boton_reiniciar.center)
        pygame.draw.rect(self.pantalla, self.COLOR_GRIS_CLARO, boton_reiniciar)
        self.pantalla.blit(texto_reiniciar, texto_reiniciar_rect)
    
    def _obtener_rect_boton_reiniciar(self) -> pygame.Rect:
        """Retorna el rectángulo del botón de reiniciar."""
        return pygame.Rect(self.VENTANA_ANCHO / 3, self.VENTANA_ALTO/2, self.VENTANA_ANCHO / 3, 50)
    
    def _escribir_resumen_final(self, titulo_juego: str, tiempo_promedio: float):
        """Escribe el resumen final de la partida."""
        with open(self.nombre_archivo_log, "a", encoding="utf-8") as archivo:
            archivo.write(f"\n--- RESUMEN DE LA PARTIDA ---\n")
            archivo.write(f"Total de movimientos de IA: {self.cantidad_movimientos_ia}\n")
            archivo.write(f"Tiempo total: {self.tiempo_total_ia:.8f} segundos\n")
            archivo.write(f"Tiempo promedio: {tiempo_promedio:.8f} segundos\n")
            archivo.write(f"Ganador: {titulo_juego}\n")
            archivo.write(f"{'='*50}\n\n")
        self.resumen_escrito = True
    
    def ejecutar(self):
        """
        Bucle principal del juego.
        Controla eventos, actualiza estado y dibuja la pantalla.
        """
        reloj = pygame.time.Clock()
        
        while True:
            # Manejar eventos
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                elif evento.type == pygame.MOUSEBUTTONDOWN:
                    pos_mouse = pygame.mouse.get_pos()
                    
                    # Pantalla de configuración
                    if (self.jugador_usuario is None or 
                        self.modo_busqueda_alfa_beta is None or 
                        self.nivel_ia_seleccionado is None):
                        self.manejar_click_configuracion(pos_mouse)
                    
                    # Pantalla de fin de juego
                    elif self.tablero.es_final(self.jugador_activo):
                        boton_reiniciar = self._obtener_rect_boton_reiniciar()
                        if boton_reiniciar.collidepoint(pos_mouse):
                            self.reiniciar_juego()
                    
                    # Juego en curso
                    else:
                        self.manejar_click_juego(pos_mouse)
            
            # Actualizar lógica del juego
            if (self.jugador_usuario is not None and 
                self.modo_busqueda_alfa_beta is not None and 
                self.nivel_ia_seleccionado is not None and
                not self.tablero.es_final(self.jugador_activo) and
                self.jugador_activo != self.jugador_usuario):
                self.ejecutar_movimiento_ia()
            
            # Dibujar pantalla
            if (self.jugador_usuario is None or 
                self.modo_busqueda_alfa_beta is None or 
                self.nivel_ia_seleccionado is None):
                self.dibujar_pantalla_configuracion()
            else:
                self.dibujar_interfaz_juego()
            
            pygame.display.flip()
            reloj.tick(60)  # 60 FPS


def main():
    """Función principal que inicia el juego."""
    try:
        juego = JuegoDamas()
        juego.ejecutar()
    except Exception as e:
        print(f"Error en el juego: {e}")
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    main()

# juego.py
import pygame
import sys
import time

import busqueda as logica

pygame.init()

# --- Configuración de la Ventana y Colores ---
VENTANA_ANCHO = 800
VENTANA_ALTO = 800

# Calcular el tamaño de la celda en base a la dimensión del tablero
CELDA_TAMANO = min(VENTANA_ANCHO, VENTANA_ALTO) // (logica.TABLERO_DIM + 2)
TABLERO_ORIGEN_X = (VENTANA_ANCHO - logica.TABLERO_DIM * CELDA_TAMANO) // 2
TABLERO_ORIGEN_Y = (VENTANA_ALTO - logica.TABLERO_DIM * CELDA_TAMANO) // 2


# Colores
COLOR_NEGRO = (0, 0, 0)
COLOR_BLANCO = (255, 255, 255)
COLOR_AZUL_OSCURO = (0, 0, 139)
COLOR_GRIS_CLARO = (211, 211, 211)
COLOR_ROJO = (255, 0, 0)
COLOR_VERDE = (0, 255, 0)

# Colores del tablero de damas (casillas claras y oscuras)
COLOR_CASILLA_CLARA = (240, 217, 181)
COLOR_CASILLA_OSCURA = (181, 136, 99)

pantalla_principal = pygame.display.set_mode((VENTANA_ANCHO, VENTANA_ALTO))
pygame.display.set_caption("Damas Chinas IA")

# Fuentes
try:
    fuente_pequena = pygame.font.Font("OpenSans-Regular.ttf", 28)
    fuente_grande = pygame.font.Font("OpenSans-Regular.ttf", 40)
    fuente_movimiento = pygame.font.Font("OpenSans-Regular.ttf", int(CELDA_TAMANO * 0.6))
except:
    print("Advertencia: No se encontró 'OpenSans-Regular.ttf'. Usando fuente por defecto.")
    fuente_pequena = pygame.font.Font(None, 28)
    fuente_grande = pygame.font.Font(None, 40)
    fuente_movimiento = pygame.font.Font(None, int(CELDA_TAMANO * 0.6))


# --- Variables del Juego ---
jugador_usuario = None
jugador_activo = None
estado_tablero = logica.tablero_inicial()
modo_busqueda_alfa_beta = None

# Variables para la interacción con el usuario
pieza_seleccionada = None
movimientos_posibles_para_seleccion = set()

# --- Bucle Principal del Juego ---
while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            sys.exit()

        if evento.type == pygame.MOUSEBUTTONDOWN:
            posicion_mouse = pygame.mouse.get_pos()

            # Lógica de selección de jugador y modo al inicio
            if jugador_usuario is None:
                # Botones de elección de jugador
                boton_blanco = pygame.Rect((VENTANA_ANCHO / 8), (VENTANA_ALTO / 2 - 80), VENTANA_ANCHO / 4, 50)
                boton_negro = pygame.Rect(5 * (VENTANA_ANCHO / 8), (VENTANA_ALTO / 2 - 80), VENTANA_ANCHO / 4, 50)
                # Botones de elección de modo IA
                boton_alfa_beta = pygame.Rect((VENTANA_ANCHO / 8), (VENTANA_ALTO / 2 + 50), VENTANA_ANCHO / 3, 40)
                boton_minimax = pygame.Rect((VENTANA_ANCHO / 2 + 20), (VENTANA_ALTO / 2 + 50), VENTANA_ANCHO / 3, 40)

                if boton_blanco.collidepoint(posicion_mouse):
                    time.sleep(0.2)
                    jugador_usuario = logica.JUGADOR_BLANCO
                    jugador_activo = logica.JUGADOR_BLANCO # Blanco siempre inicia
                elif boton_negro.collidepoint(posicion_mouse):
                    time.sleep(0.2)
                    jugador_usuario = logica.JUGADOR_NEGRO
                    jugador_activo = logica.JUGADOR_BLANCO # Blanco siempre inicia, IA jugará primero si usuario es Negro
                elif boton_alfa_beta.collidepoint(posicion_mouse):
                    modo_busqueda_alfa_beta = True
                elif boton_minimax.collidepoint(posicion_mouse):
                    modo_busqueda_alfa_beta = False
            
            # Lógica para reiniciar el juego
            elif jugador_activo is not None and logica.es_final(estado_tablero, jugador_activo):
                boton_reiniciar = pygame.Rect(VENTANA_ANCHO / 3, VENTANA_ALTO - 65, VENTANA_ANCHO / 3, 50)
                if boton_reiniciar.collidepoint(posicion_mouse):
                    time.sleep(0.2)
                    jugador_usuario = None
                    jugador_activo = None
                    estado_tablero = logica.tablero_inicial()
                    pieza_seleccionada = None
                    movimientos_posibles_para_seleccion = set()
                    modo_busqueda_alfa_beta = None

            # Lógica para el movimiento del usuario (solo si es su turno y el juego no ha terminado)
            elif jugador_activo is not None and jugador_usuario == jugador_activo and not logica.es_final(estado_tablero, jugador_activo):
                col = (posicion_mouse[0] - TABLERO_ORIGEN_X) // CELDA_TAMANO
                row = (posicion_mouse[1] - TABLERO_ORIGEN_Y) // CELDA_TAMANO

                if 0 <= row < logica.TABLERO_DIM and 0 <= col < logica.TABLERO_DIM and (row + col) % 2 != 0:
                    
                    if pieza_seleccionada:
                        movimiento_encontrado = None
                        for (p_origen, p_destino) in movimientos_posibles_para_seleccion:
                            if p_origen == pieza_seleccionada and p_destino == (row, col):
                                movimiento_encontrado = (p_origen, p_destino)
                                break
                        
                        if movimiento_encontrado:
                            estado_tablero = logica.aplicar_movimiento(estado_tablero, movimiento_encontrado)
                            pieza_seleccionada = None
                            movimientos_posibles_para_seleccion = set()
                            jugador_activo = logica.obtener_jugador_oponente(jugador_activo) # ¡Cambio de turno!
                        else:
                            pieza_en_celda = estado_tablero[row][col]
                            es_pieza_usuario = (jugador_usuario == logica.JUGADOR_BLANCO and (pieza_en_celda == logica.JUGADOR_BLANCO or pieza_en_celda == logica.DAMA_BLANCA)) or \
                                               (jugador_usuario == logica.JUGADOR_NEGRO and (pieza_en_celda == logica.JUGADOR_NEGRO or pieza_en_celda == logica.DAMA_NEGRA))
                            
                            if es_pieza_usuario:
                                pieza_seleccionada = (row, col)
                                todos_movimientos = logica.movimientos_disponibles(estado_tablero, jugador_activo)
                                movimientos_posibles_para_seleccion = {
                                    mov for mov in todos_movimientos if mov[0] == pieza_seleccionada
                                }
                            else:
                                pieza_seleccionada = None
                                movimientos_posibles_para_seleccion = set()

                    else:
                        pieza_en_celda = estado_tablero[row][col]
                        es_pieza_usuario = (jugador_usuario == logica.JUGADOR_BLANCO and (pieza_en_celda == logica.JUGADOR_BLANCO or pieza_en_celda == logica.DAMA_BLANCA)) or \
                                           (jugador_usuario == logica.JUGADOR_NEGRO and (pieza_en_celda == logica.JUGADOR_NEGRO or pieza_en_celda == logica.DAMA_NEGRA))

                        if es_pieza_usuario:
                            pieza_seleccionada = (row, col)
                            todos_movimientos = logica.movimientos_disponibles(estado_tablero, jugador_activo)
                            movimientos_posibles_para_seleccion = {
                                mov for mov in todos_movimientos if mov[0] == pieza_seleccionada
                            }
                        else:
                            pieza_seleccionada = None
                            movimientos_posibles_para_seleccion = set()
                else: # Clic fuera del tablero o en casilla clara
                    pieza_seleccionada = None
                    movimientos_posibles_para_seleccion = set()


    pantalla_principal.fill(COLOR_NEGRO)

    # --- Pantalla de Inicio (Selección de Jugador y Modo) ---
    if jugador_usuario is None:
        titulo_juego = fuente_grande.render("Damas Chinas IA", True, COLOR_AZUL_OSCURO)
        tituloRect = titulo_juego.get_rect(center=(VENTANA_ANCHO / 2, 50))
        pantalla_principal.blit(titulo_juego, tituloRect)

        sub_titulo = fuente_pequena.render(f"Tablero {logica.TABLERO_DIM}x{logica.TABLERO_DIM}", True, COLOR_BLANCO)
        sub_titulo_rect = sub_titulo.get_rect(center=(VENTANA_ANCHO / 2, 90))
        pantalla_principal.blit(sub_titulo, sub_titulo_rect)


        boton_blanco = pygame.Rect((VENTANA_ANCHO / 8), (VENTANA_ALTO / 2 - 80), VENTANA_ANCHO / 4, 50)
        texto_blanco = fuente_pequena.render(" Jugar con Blancas ", True, COLOR_NEGRO)
        texto_blancoRect = texto_blanco.get_rect(center=boton_blanco.center)
        pygame.draw.rect(pantalla_principal, COLOR_GRIS_CLARO, boton_blanco)
        pantalla_principal.blit(texto_blanco, texto_blancoRect)

        boton_negro = pygame.Rect(5 * (VENTANA_ANCHO / 8), (VENTANA_ALTO / 2 - 80), VENTANA_ANCHO / 4, 50)
        texto_negro = fuente_pequena.render(" Jugar con Negras ", True, COLOR_NEGRO)
        texto_negroRect = texto_negro.get_rect(center=boton_negro.center)
        pygame.draw.rect(pantalla_principal, COLOR_GRIS_CLARO, boton_negro)
        pantalla_principal.blit(texto_negro, texto_negroRect)

        boton_alfa_beta = pygame.Rect((VENTANA_ANCHO / 8), (VENTANA_ALTO / 2 + 50), VENTANA_ANCHO / 3, 40)
        texto_alfa_beta = fuente_pequena.render("Poda Alfa-Beta", True, COLOR_NEGRO)
        texto_alfa_betaRect = texto_alfa_beta.get_rect(center=boton_alfa_beta.center)
        pygame.draw.rect(pantalla_principal, COLOR_GRIS_CLARO, boton_alfa_beta)
        pantalla_principal.blit(texto_alfa_beta, texto_alfa_betaRect)

        boton_minimax = pygame.Rect((VENTANA_ANCHO / 2 + 20), (VENTANA_ALTO / 2 + 50), VENTANA_ANCHO / 3, 40)
        texto_minimax = fuente_pequena.render("Minimax Puro", True, COLOR_NEGRO)
        texto_minimaxRect = texto_minimax.get_rect(center=boton_minimax.center)
        pygame.draw.rect(pantalla_principal, COLOR_GRIS_CLARO, boton_minimax)
        pantalla_principal.blit(texto_minimax, texto_minimaxRect)

        if modo_busqueda_alfa_beta is not None:
            modo_texto = "Poda Alfa-Beta" if modo_busqueda_alfa_beta else "Minimax Puro"
            modo_seleccionado_texto = fuente_pequena.render(f"Modo IA: {modo_texto}", True, COLOR_BLANCO)
            modo_seleccionado_rect = modo_seleccionado_texto.get_rect(center=(VENTANA_ANCHO / 2, VENTANA_ALTO - 50))
            pantalla_principal.blit(modo_seleccionado_texto, modo_seleccionado_rect)

    else:
        for r in range(logica.TABLERO_DIM):
            for c in range(logica.TABLERO_DIM):
                rect = pygame.Rect(
                    TABLERO_ORIGEN_X + c * CELDA_TAMANO,
                    TABLERO_ORIGEN_Y + r * CELDA_TAMANO,
                    CELDA_TAMANO, CELDA_TAMANO
                )
                color_casilla = COLOR_CASILLA_OSCURA if (r + c) % 2 != 0 else COLOR_CASILLA_CLARA
                pygame.draw.rect(pantalla_principal, color_casilla, rect)

                if pieza_seleccionada == (r, c):
                    pygame.draw.rect(pantalla_principal, COLOR_ROJO, rect, 4)

                for (origen_mov, destino_mov) in movimientos_posibles_para_seleccion:
                    if destino_mov == (r, c):
                        pygame.draw.circle(pantalla_principal, COLOR_VERDE, rect.center, CELDA_TAMANO // 8)

                pieza = estado_tablero[r][c]
                if pieza == logica.JUGADOR_BLANCO:
                    pygame.draw.circle(pantalla_principal, COLOR_BLANCO, rect.center, CELDA_TAMANO // 3)
                elif pieza == logica.JUGADOR_NEGRO:
                    pygame.draw.circle(pantalla_principal, COLOR_NEGRO, rect.center, CELDA_TAMANO // 3)
                elif pieza == logica.DAMA_BLANCA:
                    pygame.draw.circle(pantalla_principal, COLOR_BLANCO, rect.center, CELDA_TAMANO // 3)
                    pygame.draw.circle(pantalla_principal, COLOR_AZUL_OSCURO, rect.center, CELDA_TAMANO // 4, 2)
                elif pieza == logica.DAMA_NEGRA:
                    pygame.draw.circle(pantalla_principal, COLOR_NEGRO, rect.center, CELDA_TAMANO // 3)
                    pygame.draw.circle(pantalla_principal, COLOR_BLANCO, rect.center, CELDA_TAMANO // 4, 2)


        ggwp = logica.es_final(estado_tablero, jugador_activo)

        if ggwp:
            ganador = logica.determinar_ganador(estado_tablero, jugador_activo)
            if ganador is None:
                titulo_juego = "¡Empate!"
            else:
                titulo_juego = f"¡{'Blancas' if ganador == logica.JUGADOR_BLANCO else 'Negras'} ganaron!"
        elif jugador_usuario == jugador_activo:
            titulo_juego = f"Tu turno: {'Blancas' if jugador_usuario == logica.JUGADOR_BLANCO else 'Negras'}"
        else:
            time.sleep(0.1)
            titulo_juego = "IA pensando..."

        titulo_render = fuente_grande.render(titulo_juego, True, COLOR_BLANCO)
        tituloRect = titulo_render.get_rect(center=(VENTANA_ANCHO / 2, 30))
        pantalla_principal.blit(titulo_render, tituloRect)

        if modo_busqueda_alfa_beta is not None:
            modo_texto = "Poda Alfa-Beta" if modo_busqueda_alfa_beta else "Minimax Puro"
            modo_info_texto = fuente_pequena.render(f"IA: {modo_texto}", True, COLOR_BLANCO)
            modo_info_rect = modo_info_texto.get_rect(center=(VENTANA_ANCHO / 2, VENTANA_ALTO - 20))
            pantalla_principal.blit(modo_info_texto, modo_info_rect)


        if modo_busqueda_alfa_beta is None:
            modo_busqueda_alfa_beta = False


        # Lógica para el movimiento de la IA
        if not ggwp and jugador_usuario != jugador_activo:
            time.sleep(0.7)
            if modo_busqueda_alfa_beta:
                movimiento_ia = logica.algoritmo_minimax_alfa_beta(estado_tablero, jugador_activo)
            else:
                movimiento_ia = logica.algoritmo_minimax(estado_tablero, jugador_activo)

            if movimiento_ia:
                estado_tablero = logica.aplicar_movimiento(estado_tablero, movimiento_ia)
                jugador_activo = logica.obtener_jugador_oponente(jugador_activo)
            else:
                print(f"La IA ({jugador_activo}) no encontró movimientos válidos.")
                # Si la IA no puede moverse, el juego debería haber terminado y declarado un ganador.
                # Si llega aquí y no hay ganador, podría ser un estado de empate o un problema en la lógica de movimientos/fin de juego.


        if ggwp:
            boton_reiniciar = pygame.Rect(VENTANA_ANCHO / 3, VENTANA_ALTO - 65, VENTANA_ANCHO / 3, 50)
            texto_reiniciar = fuente_pequena.render("Volver a Jugar", True, COLOR_NEGRO)
            texto_reiniciarRect = texto_reiniciar.get_rect(center=boton_reiniciar.center)
            pygame.draw.rect(pantalla_principal, COLOR_GRIS_CLARO, boton_reiniciar)
            pantalla_principal.blit(texto_reiniciar, texto_reiniciarRect)

    pygame.display.flip()
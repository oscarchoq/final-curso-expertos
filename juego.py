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

# Color para resaltar la última ficha movida
COLOR_RESALTADO_ULTIMO_MOVIMIENTO = (255, 215, 0)  # Dorado
COLOR_RESALTADO_ORIGEN = (255, 165, 0)  # Naranja para origen
COLOR_RESALTADO_DESTINO = (255, 215, 0)  # Dorado para destino

pantalla_principal = pygame.display.set_mode((VENTANA_ANCHO, VENTANA_ALTO))
pygame.display.set_caption("Damas IA")

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
nivel_ia_seleccionado = None

# Variables para la interacción con el usuario
pieza_seleccionada = None
movimientos_posibles_para_seleccion = set()

# Variables para resaltar la última ficha movida
ultimo_movimiento_origen = None
ultimo_movimiento_destino = None
informacion_ultimo_movimiento = ""
ultimo_movimiento_fue_ia = False

def obtener_informacion_movimiento(tablero_antes, tablero_despues, movimiento):
    """
    Determina información sobre el movimiento realizado para mostrar al usuario
    """
    origen, destino = movimiento
    pieza_movida = tablero_despues[destino[0]][destino[1]]
    
    # Verificar si se convirtió en dama
    se_convirtio_dama = False
    if origen[0] == 0 and pieza_movida == logica.DAMA_NEGRA:
        se_convirtio_dama = True
    elif origen[0] == logica.TABLERO_DIM - 1 and pieza_movida == logica.DAMA_BLANCA:
        se_convirtio_dama = True
    
    # Contar piezas capturadas
    piezas_antes = sum(row.count(logica.JUGADOR_BLANCO) + row.count(logica.JUGADOR_NEGRO) + 
                      row.count(logica.DAMA_BLANCA) + row.count(logica.DAMA_NEGRA) for row in tablero_antes)
    piezas_despues = sum(row.count(logica.JUGADOR_BLANCO) + row.count(logica.JUGADOR_NEGRO) + 
                        row.count(logica.DAMA_BLANCA) + row.count(logica.DAMA_NEGRA) for row in tablero_despues)
    
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

# --- Bucle Principal del Juego ---
while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            sys.exit()

        if evento.type == pygame.MOUSEBUTTONDOWN:
            posicion_mouse = pygame.mouse.get_pos()

            # Lógica de selección de jugador y modo al inicio
            if jugador_usuario is None or modo_busqueda_alfa_beta is None or nivel_ia_seleccionado is None:
                # Botones de elección de jugador
                boton_blanco = pygame.Rect((VENTANA_ANCHO / 8), (VENTANA_ALTO / 2 - 120), VENTANA_ANCHO / 4, 40)
                boton_negro = pygame.Rect(5 * (VENTANA_ANCHO / 8), (VENTANA_ALTO / 2 - 120), VENTANA_ANCHO / 4, 40)
                
                # Botones de elección de modo IA
                boton_alfa_beta = pygame.Rect((VENTANA_ANCHO / 8), (VENTANA_ALTO / 2 - 70), VENTANA_ANCHO / 3, 35)
                boton_minimax = pygame.Rect((VENTANA_ANCHO / 2 + 20), (VENTANA_ALTO / 2 - 70), VENTANA_ANCHO / 3, 35)
                
                # Botones de niveles de dificultad
                botones_nivel = []
                for i in range(1, 6):
                    x = (VENTANA_ANCHO / 6) + (i - 1) * (VENTANA_ANCHO / 6)
                    y = VENTANA_ALTO / 2 - 20
                    botones_nivel.append(pygame.Rect(x - 25, y, 50, 30))

                if boton_blanco.collidepoint(posicion_mouse):
                    time.sleep(0.2)
                    jugador_usuario = logica.JUGADOR_BLANCO
                    jugador_activo = logica.JUGADOR_BLANCO
                elif boton_negro.collidepoint(posicion_mouse):
                    time.sleep(0.2)
                    jugador_usuario = logica.JUGADOR_NEGRO
                    jugador_activo = logica.JUGADOR_BLANCO
                elif boton_alfa_beta.collidepoint(posicion_mouse):
                    modo_busqueda_alfa_beta = True
                elif boton_minimax.collidepoint(posicion_mouse):
                    modo_busqueda_alfa_beta = False
                else:
                    # Verificar clicks en botones de nivel
                    for i, boton in enumerate(botones_nivel):
                        if boton.collidepoint(posicion_mouse):
                            nivel_ia_seleccionado = i + 1
                            logica.establecer_nivel_ia(i + 1)
                            break

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
                    nivel_ia_seleccionado = None
                    # Reiniciar también el resaltado del último movimiento
                    ultimo_movimiento_origen = None
                    ultimo_movimiento_destino = None
                    informacion_ultimo_movimiento = ""
                    ultimo_movimiento_fue_ia = False

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
                            tablero_antes = [fila[:] for fila in estado_tablero]  # Copia del tablero antes del movimiento
                            estado_tablero = logica.aplicar_movimiento(estado_tablero, movimiento_encontrado)
                            # Actualizar el resaltado del último movimiento
                            ultimo_movimiento_origen = movimiento_encontrado[0]
                            ultimo_movimiento_destino = movimiento_encontrado[1]
                            informacion_ultimo_movimiento = obtener_informacion_movimiento(tablero_antes, estado_tablero, movimiento_encontrado)
                            ultimo_movimiento_fue_ia = False
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
    if jugador_usuario is None or modo_busqueda_alfa_beta is None or nivel_ia_seleccionado is None:
        titulo_juego = fuente_grande.render("Damas IA", True, COLOR_AZUL_OSCURO)
        tituloRect = titulo_juego.get_rect(center=(VENTANA_ANCHO / 2, 50))
        pantalla_principal.blit(titulo_juego, tituloRect)

        sub_titulo = fuente_pequena.render(f"Tablero {logica.TABLERO_DIM}x{logica.TABLERO_DIM}", True, COLOR_BLANCO)
        sub_titulo_rect = sub_titulo.get_rect(center=(VENTANA_ANCHO / 2, 90))
        pantalla_principal.blit(sub_titulo, sub_titulo_rect)

        # Sección de color del jugador
        seccion_jugador = fuente_pequena.render("Selecciona tu color:", True, COLOR_BLANCO)
        seccion_jugador_rect = seccion_jugador.get_rect(center=(VENTANA_ANCHO / 2, VENTANA_ALTO / 2 - 150))
        pantalla_principal.blit(seccion_jugador, seccion_jugador_rect)

        boton_blanco = pygame.Rect((VENTANA_ANCHO / 8), (VENTANA_ALTO / 2 - 120), VENTANA_ANCHO / 4, 40)
        texto_blanco = fuente_pequena.render("Blancas", True, COLOR_NEGRO)
        texto_blancoRect = texto_blanco.get_rect(center=boton_blanco.center)
        color_boton = COLOR_VERDE if jugador_usuario == logica.JUGADOR_BLANCO else COLOR_GRIS_CLARO
        pygame.draw.rect(pantalla_principal, color_boton, boton_blanco)
        pantalla_principal.blit(texto_blanco, texto_blancoRect)

        boton_negro = pygame.Rect(5 * (VENTANA_ANCHO / 8), (VENTANA_ALTO / 2 - 120), VENTANA_ANCHO / 4, 40)
        texto_negro = fuente_pequena.render("Negras", True, COLOR_NEGRO)
        texto_negroRect = texto_negro.get_rect(center=boton_negro.center)
        color_boton = COLOR_VERDE if jugador_usuario == logica.JUGADOR_NEGRO else COLOR_GRIS_CLARO
        pygame.draw.rect(pantalla_principal, color_boton, boton_negro)
        pantalla_principal.blit(texto_negro, texto_negroRect)

        # Sección de algoritmo
        seccion_algoritmo = fuente_pequena.render("Algoritmo de IA:", True, COLOR_BLANCO)
        seccion_algoritmo_rect = seccion_algoritmo.get_rect(center=(VENTANA_ANCHO / 2, VENTANA_ALTO / 2 - 100))
        pantalla_principal.blit(seccion_algoritmo, seccion_algoritmo_rect)

        boton_alfa_beta = pygame.Rect((VENTANA_ANCHO / 8), (VENTANA_ALTO / 2 - 70), VENTANA_ANCHO / 3, 35)
        texto_alfa_beta = fuente_pequena.render("Alfa-Beta", True, COLOR_NEGRO)
        texto_alfa_betaRect = texto_alfa_beta.get_rect(center=boton_alfa_beta.center)
        color_boton = COLOR_VERDE if modo_busqueda_alfa_beta == True else COLOR_GRIS_CLARO
        pygame.draw.rect(pantalla_principal, color_boton, boton_alfa_beta)
        pantalla_principal.blit(texto_alfa_beta, texto_alfa_betaRect)

        boton_minimax = pygame.Rect((VENTANA_ANCHO / 2 + 20), (VENTANA_ALTO / 2 - 70), VENTANA_ANCHO / 3, 35)
        texto_minimax = fuente_pequena.render("Minimax", True, COLOR_NEGRO)
        texto_minimaxRect = texto_minimax.get_rect(center=boton_minimax.center)
        color_boton = COLOR_VERDE if modo_busqueda_alfa_beta == False else COLOR_GRIS_CLARO
        pygame.draw.rect(pantalla_principal, color_boton, boton_minimax)
        pantalla_principal.blit(texto_minimax, texto_minimaxRect)

        # Sección de nivel de dificultad
        seccion_nivel = fuente_pequena.render("Nivel de dificultad:", True, COLOR_BLANCO)
        seccion_nivel_rect = seccion_nivel.get_rect(center=(VENTANA_ANCHO / 2, VENTANA_ALTO / 2 - 50))
        pantalla_principal.blit(seccion_nivel, seccion_nivel_rect)

        # Botones de niveles
        for i in range(1, 6):
            x = (VENTANA_ANCHO / 6) + (i - 1) * (VENTANA_ANCHO / 6)
            y = VENTANA_ALTO / 2 - 20
            boton_nivel = pygame.Rect(x - 25, y, 50, 30)
            
            color_boton = COLOR_VERDE if nivel_ia_seleccionado == i else COLOR_GRIS_CLARO
            pygame.draw.rect(pantalla_principal, color_boton, boton_nivel)
            
            texto_nivel = fuente_pequena.render(str(i), True, COLOR_NEGRO)
            texto_nivel_rect = texto_nivel.get_rect(center=boton_nivel.center)
            pantalla_principal.blit(texto_nivel, texto_nivel_rect)

        # Mostrar información del nivel seleccionado
        if nivel_ia_seleccionado is not None:
            info_nivel = logica.NIVELES_DIFICULTAD[nivel_ia_seleccionado]
            texto_info = f"Nivel {nivel_ia_seleccionado}: {info_nivel['nombre']}"
            info_texto = fuente_pequena.render(texto_info, True, COLOR_BLANCO)
            info_rect = info_texto.get_rect(center=(VENTANA_ANCHO / 2, VENTANA_ALTO / 2 + 20))
            pantalla_principal.blit(info_texto, info_rect)
            
            descripcion_texto = info_nivel['descripcion']
            desc_render = fuente_pequena.render(descripcion_texto, True, COLOR_BLANCO)
            desc_rect = desc_render.get_rect(center=(VENTANA_ANCHO / 2, VENTANA_ALTO / 2 + 50))
            pantalla_principal.blit(desc_render, desc_rect)

        # Verificar si todo está seleccionado
        if jugador_usuario is not None and modo_busqueda_alfa_beta is not None and nivel_ia_seleccionado is not None:
            empezar_texto = fuente_grande.render("¡LISTO PARA JUGAR!", True, COLOR_VERDE)
            empezar_rect = empezar_texto.get_rect(center=(VENTANA_ANCHO / 2, VENTANA_ALTO - 100))
            pantalla_principal.blit(empezar_texto, empezar_rect)

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

                # Resaltar la última ficha movida (origen y destino con colores diferentes)
                if ultimo_movimiento_origen == (r, c):
                    pygame.draw.rect(pantalla_principal, COLOR_RESALTADO_ORIGEN, rect, 6)
                elif ultimo_movimiento_destino == (r, c):
                    pygame.draw.rect(pantalla_principal, COLOR_RESALTADO_DESTINO, rect, 6)

                # Resaltar la pieza seleccionada por el usuario
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
            titulo_juego = "IA pensando..."
            titulo_render = fuente_grande.render(titulo_juego, True, COLOR_BLANCO)
            tituloRect = titulo_render.get_rect(center=(VENTANA_ANCHO / 2, 30))
            pantalla_principal.blit(titulo_render, tituloRect)
            pygame.display.flip()
            time.sleep(0.1)

        if modo_busqueda_alfa_beta is not None and nivel_ia_seleccionado is not None:
            info_nivel = logica.obtener_nivel_actual()
            modo_texto = "Alfa-Beta" if modo_busqueda_alfa_beta else "Minimax"
            info_completa = f"IA: {modo_texto} | Nivel {nivel_ia_seleccionado}: {info_nivel['nombre']}"
            modo_info_texto = fuente_pequena.render(info_completa, True, COLOR_BLANCO)
            modo_info_rect = modo_info_texto.get_rect(center=(VENTANA_ANCHO / 2, VENTANA_ALTO - 40))
            pantalla_principal.blit(modo_info_texto, modo_info_rect)

        # Mostrar información del último movimiento si existe
        if informacion_ultimo_movimiento:
            prefijo = "IA: " if ultimo_movimiento_fue_ia else "Tú: "
            texto_completo = prefijo + informacion_ultimo_movimiento
            info_movimiento_texto = fuente_pequena.render(texto_completo, True, COLOR_RESALTADO_DESTINO)
            info_movimiento_rect = info_movimiento_texto.get_rect(center=(VENTANA_ANCHO / 2, VENTANA_ALTO - 20))
            pantalla_principal.blit(info_movimiento_texto, info_movimiento_rect)


        if modo_busqueda_alfa_beta is None:
            modo_busqueda_alfa_beta = False


        # Lógica para el movimiento de la IA
        if not ggwp and jugador_usuario != jugador_activo:
            # Mostrar mensaje antes de sleep para que el usuario lo vea
            titulo_juego = "IA pensando..."
            titulo_render = fuente_grande.render(titulo_juego, True, COLOR_BLANCO)
            tituloRect = titulo_render.get_rect(center=(VENTANA_ANCHO / 2, 30))
            pantalla_principal.blit(titulo_render, tituloRect)
            pygame.display.flip()
            
            # Usar tiempo de pensamiento según el nivel
            tiempo_pensamiento = logica.obtener_tiempo_pensamiento()
            time.sleep(tiempo_pensamiento)
            
            if modo_busqueda_alfa_beta:
                movimiento_ia = logica.algoritmo_minimax_alfa_beta(estado_tablero, jugador_activo)
            else:
                movimiento_ia = logica.algoritmo_minimax(estado_tablero, jugador_activo)

            if movimiento_ia:
                # Actualizar el resaltado del último movimiento para la IA
                tablero_antes = [fila[:] for fila in estado_tablero]  # Copia del tablero antes del movimiento
                ultimo_movimiento_origen = movimiento_ia[0]
                ultimo_movimiento_destino = movimiento_ia[1]
                estado_tablero = logica.aplicar_movimiento(estado_tablero, movimiento_ia)
                informacion_ultimo_movimiento = obtener_informacion_movimiento(tablero_antes, estado_tablero, movimiento_ia)
                ultimo_movimiento_fue_ia = True
                jugador_activo = logica.obtener_jugador_oponente(jugador_activo)
            else:
                print(f"La IA ({jugador_activo}) no encontró movimientos válidos.")
        if ggwp:
            boton_reiniciar = pygame.Rect(VENTANA_ANCHO / 3, VENTANA_ALTO - 65, VENTANA_ANCHO / 3, 50)
            texto_reiniciar = fuente_pequena.render("Volver a Jugar", True, COLOR_NEGRO)
            texto_reiniciarRect = texto_reiniciar.get_rect(center=boton_reiniciar.center)
            pygame.draw.rect(pantalla_principal, COLOR_GRIS_CLARO, boton_reiniciar)
            pantalla_principal.blit(texto_reiniciar, texto_reiniciarRect)

    pygame.display.flip()
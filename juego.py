# juego.py
import pygame
import sys
import time
import os

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

# Variables para el seguimiento del tiempo de la IA
tiempo_total_ia = 0.0
cantidad_movimientos_ia = 0
tiempos_ia = []  # Lista para almacenar todos los tiempos
resumen_escrito = False  # Variable para controlar si ya se escribió el resumen de la partida

# Crear la carpeta LogTime si no existe
if not os.path.exists("LogTime"):
    os.makedirs("LogTime")

# Generar nombre único para el archivo de log con fecha y hora
timestamp = time.strftime("%Y%m%d_%H%M%S")
nombre_archivo_log = f"LogTime/logtime_{timestamp}.txt"

# Inicializar el archivo de log
with open(nombre_archivo_log, "w", encoding="utf-8") as archivo:
    archivo.write("=== LOG DE TIEMPOS DE LA IA - JUEGO DE DAMAS ===\n")
    archivo.write(f"Inicio de sesión: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    archivo.write("="*50 + "\n\n")

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
                # Dimensiones consistentes con el dibujo
                boton_ancho = 150
                boton_alto = 45
                separacion = 60
                
                # Botones de elección de jugador
                boton_blanco = pygame.Rect((VENTANA_ANCHO / 2 - boton_ancho - separacion/2), 210, boton_ancho, boton_alto)
                boton_negro = pygame.Rect((VENTANA_ANCHO / 2 + separacion/2), 210, boton_ancho, boton_alto)
                
                # Botones de elección de modo IA
                boton_alfa_beta = pygame.Rect((VENTANA_ANCHO / 2 - boton_ancho - separacion/2), 330, boton_ancho, boton_alto)
                boton_minimax = pygame.Rect((VENTANA_ANCHO / 2 + separacion/2), 330, boton_ancho, boton_alto)
                
                # Botones de niveles de dificultad
                botones_nivel = []
                botones_por_fila = 5
                boton_nivel_tamano = 60
                espacio_entre_botones = 20
                inicio_x = VENTANA_ANCHO / 2 - (botones_por_fila * boton_nivel_tamano + (botones_por_fila - 1) * espacio_entre_botones) / 2
                
                for i in range(1, 6):
                    x = inicio_x + (i - 1) * (boton_nivel_tamano + espacio_entre_botones)
                    y = 450
                    botones_nivel.append(pygame.Rect(x, y, boton_nivel_tamano, boton_nivel_tamano))

                if boton_blanco.collidepoint(posicion_mouse):
                    jugador_usuario = logica.JUGADOR_BLANCO
                    jugador_activo = logica.JUGADOR_BLANCO
                elif boton_negro.collidepoint(posicion_mouse):
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
                            break

            # Lógica para reiniciar el juego
            elif jugador_activo is not None and logica.es_final(estado_tablero, jugador_activo):
                boton_reiniciar = pygame.Rect(VENTANA_ANCHO / 3, VENTANA_ALTO - 65, VENTANA_ANCHO / 3, 50)
                if boton_reiniciar.collidepoint(posicion_mouse):
                    # Escribir separador en el archivo antes de reiniciar
                    if cantidad_movimientos_ia > 0:
                        with open(nombre_archivo_log, "a", encoding="utf-8") as archivo:
                            archivo.write(f"\n--- NUEVA PARTIDA ---\n")
                            archivo.write(f"Inicio: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    
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
                    # Reiniciar variables de seguimiento del tiempo
                    tiempo_total_ia = 0.0
                    cantidad_movimientos_ia = 0
                    tiempos_ia = []
                    resumen_escrito = False

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
        # Título principal
        titulo_juego = fuente_grande.render("Damas IA", True, COLOR_AZUL_OSCURO)
        tituloRect = titulo_juego.get_rect(center=(VENTANA_ANCHO / 2, 80))
        pantalla_principal.blit(titulo_juego, tituloRect)

        sub_titulo = fuente_pequena.render(f"Tablero {logica.TABLERO_DIM}x{logica.TABLERO_DIM}", True, COLOR_BLANCO)
        sub_titulo_rect = sub_titulo.get_rect(center=(VENTANA_ANCHO / 2, 120))
        pantalla_principal.blit(sub_titulo, sub_titulo_rect)

        # Sección 1: Selección de color del jugador
        seccion_jugador = fuente_pequena.render("1. Selecciona tu color:", True, COLOR_BLANCO)
        seccion_jugador_rect = seccion_jugador.get_rect(center=(VENTANA_ANCHO / 2, 180))
        pantalla_principal.blit(seccion_jugador, seccion_jugador_rect)

        # Botones de color centrados y mejor espaciados
        boton_ancho = 150
        boton_alto = 45
        separacion = 60
        
        boton_blanco = pygame.Rect((VENTANA_ANCHO / 2 - boton_ancho - separacion/2), 210, boton_ancho, boton_alto)
        texto_blanco = fuente_pequena.render("Blancas", True, COLOR_NEGRO)
        texto_blancoRect = texto_blanco.get_rect(center=boton_blanco.center)
        color_boton = COLOR_VERDE if jugador_usuario == logica.JUGADOR_BLANCO else COLOR_GRIS_CLARO
        pygame.draw.rect(pantalla_principal, color_boton, boton_blanco)
        pygame.draw.rect(pantalla_principal, COLOR_NEGRO, boton_blanco, 2)
        pantalla_principal.blit(texto_blanco, texto_blancoRect)

        boton_negro = pygame.Rect((VENTANA_ANCHO / 2 + separacion/2), 210, boton_ancho, boton_alto)
        texto_negro = fuente_pequena.render("Negras", True, COLOR_NEGRO)
        texto_negroRect = texto_negro.get_rect(center=boton_negro.center)
        color_boton = COLOR_VERDE if jugador_usuario == logica.JUGADOR_NEGRO else COLOR_GRIS_CLARO
        pygame.draw.rect(pantalla_principal, color_boton, boton_negro)
        pygame.draw.rect(pantalla_principal, COLOR_NEGRO, boton_negro, 2)
        pantalla_principal.blit(texto_negro, texto_negroRect)

        # Sección 2: Algoritmo de IA
        seccion_algoritmo = fuente_pequena.render("2. Selecciona el algoritmo:", True, COLOR_BLANCO)
        seccion_algoritmo_rect = seccion_algoritmo.get_rect(center=(VENTANA_ANCHO / 2, 300))
        pantalla_principal.blit(seccion_algoritmo, seccion_algoritmo_rect)

        boton_alfa_beta = pygame.Rect((VENTANA_ANCHO / 2 - boton_ancho - separacion/2), 330, boton_ancho, boton_alto)
        texto_alfa_beta = fuente_pequena.render("Alfa-Beta", True, COLOR_NEGRO)
        texto_alfa_betaRect = texto_alfa_beta.get_rect(center=boton_alfa_beta.center)
        color_boton = COLOR_VERDE if modo_busqueda_alfa_beta == True else COLOR_GRIS_CLARO
        pygame.draw.rect(pantalla_principal, color_boton, boton_alfa_beta)
        pygame.draw.rect(pantalla_principal, COLOR_NEGRO, boton_alfa_beta, 2)
        pantalla_principal.blit(texto_alfa_beta, texto_alfa_betaRect)

        boton_minimax = pygame.Rect((VENTANA_ANCHO / 2 + separacion/2), 330, boton_ancho, boton_alto)
        texto_minimax = fuente_pequena.render("Minimax", True, COLOR_NEGRO)
        texto_minimaxRect = texto_minimax.get_rect(center=boton_minimax.center)
        color_boton = COLOR_VERDE if modo_busqueda_alfa_beta == False else COLOR_GRIS_CLARO
        pygame.draw.rect(pantalla_principal, color_boton, boton_minimax)
        pygame.draw.rect(pantalla_principal, COLOR_NEGRO, boton_minimax, 2)
        pantalla_principal.blit(texto_minimax, texto_minimaxRect)

        # Sección 3: Nivel de dificultad
        seccion_nivel = fuente_pequena.render("3. Selecciona la dificultad:", True, COLOR_BLANCO)
        seccion_nivel_rect = seccion_nivel.get_rect(center=(VENTANA_ANCHO / 2, 420))
        pantalla_principal.blit(seccion_nivel, seccion_nivel_rect)

        # Botones de niveles
        botones_por_fila = 5
        boton_nivel_tamano = 60
        espacio_entre_botones = 20
        inicio_x = VENTANA_ANCHO / 2 - (botones_por_fila * boton_nivel_tamano + (botones_por_fila - 1) * espacio_entre_botones) / 2
        
        for i in range(1, 6):
            x = inicio_x + (i - 1) * (boton_nivel_tamano + espacio_entre_botones)
            y = 450
            boton_nivel = pygame.Rect(x, y, boton_nivel_tamano, boton_nivel_tamano)
            
            color_boton = COLOR_VERDE if nivel_ia_seleccionado == i else COLOR_GRIS_CLARO
            pygame.draw.rect(pantalla_principal, color_boton, boton_nivel)
            pygame.draw.rect(pantalla_principal, COLOR_NEGRO, boton_nivel, 2)
            
            texto_nivel = fuente_pequena.render(str(i), True, COLOR_NEGRO)
            texto_nivel_rect = texto_nivel.get_rect(center=boton_nivel.center)
            pantalla_principal.blit(texto_nivel, texto_nivel_rect)



        # Verificar si todo está seleccionado
        if jugador_usuario is not None and modo_busqueda_alfa_beta is not None and nivel_ia_seleccionado is not None:
            empezar_texto = fuente_grande.render("¡LISTO PARA JUGAR!", True, COLOR_VERDE)
            empezar_rect = empezar_texto.get_rect(center=(VENTANA_ANCHO / 2, 550))
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
            
            # Mostrar estadísticas de tiempo de la IA
            if cantidad_movimientos_ia > 0:
                tiempo_promedio = tiempo_total_ia / cantidad_movimientos_ia
                estadisticas_texto = f"IA realizó {cantidad_movimientos_ia} movimientos"
                tiempo_texto = f"Tiempo promedio: {tiempo_promedio:.8f} segundos"
                
                estadisticas_render = fuente_pequena.render(estadisticas_texto, True, COLOR_BLANCO)
                tiempo_render = fuente_pequena.render(tiempo_texto, True, COLOR_BLANCO)
                
                estadisticas_rect = estadisticas_render.get_rect(center=(VENTANA_ANCHO / 2, 70))
                tiempo_rect = tiempo_render.get_rect(center=(VENTANA_ANCHO / 2, 100))
                
                pantalla_principal.blit(estadisticas_render, estadisticas_rect)
                pantalla_principal.blit(tiempo_render, tiempo_rect)
                
                # Escribir resumen final en el archivo solo una vez
                if not resumen_escrito:
                    with open(nombre_archivo_log, "a", encoding="utf-8") as archivo:
                        archivo.write(f"\n--- RESUMEN DE LA PARTIDA ---\n")
                        archivo.write(f"Total de movimientos de IA: {cantidad_movimientos_ia}\n")
                        archivo.write(f"Tiempo total: {tiempo_total_ia:.8f} segundos\n")
                        archivo.write(f"Tiempo promedio: {tiempo_promedio:.8f} segundos\n")
                        archivo.write(f"Ganador: {titulo_juego}\n")
                        archivo.write(f"{'='*50}\n\n")
                    resumen_escrito = True
        elif jugador_usuario == jugador_activo:
            titulo_juego = f"Tu turno: {'Blancas' if jugador_usuario == logica.JUGADOR_BLANCO else 'Negras'}"
        else:
            titulo_juego = "IA pensando..."
            titulo_render = fuente_grande.render(titulo_juego, True, COLOR_BLANCO)
            tituloRect = titulo_render.get_rect(center=(VENTANA_ANCHO / 2, 30))
            pantalla_principal.blit(titulo_render, tituloRect)
            pygame.display.flip()

        if modo_busqueda_alfa_beta is not None and nivel_ia_seleccionado is not None:
            modo_texto = "Alfa-Beta" if modo_busqueda_alfa_beta else "Minimax"
            info_completa = f"IA: {modo_texto} | Nivel {nivel_ia_seleccionado}"
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
            # Mostrar mensaje antes de que la IA piense
            titulo_juego = "IA pensando..."
            titulo_render = fuente_grande.render(titulo_juego, True, COLOR_BLANCO)
            tituloRect = titulo_render.get_rect(center=(VENTANA_ANCHO / 2, 30))
            pantalla_principal.blit(titulo_render, tituloRect)
            pygame.display.flip()
            
            # Medir el tiempo que tarda la IA en pensar
            tiempo_inicio = time.time()
            
            if modo_busqueda_alfa_beta:
                movimiento_ia = logica.algoritmo_minimax_alfa_beta(estado_tablero, jugador_activo)
            else:
                movimiento_ia = logica.algoritmo_minimax(estado_tablero, jugador_activo)
            
            tiempo_fin = time.time()
            tiempo_movimiento = tiempo_fin - tiempo_inicio
            
            # Registrar el tiempo en las variables y en el archivo
            tiempo_total_ia += tiempo_movimiento
            cantidad_movimientos_ia += 1
            tiempos_ia.append(tiempo_movimiento)
            
            # Escribir el tiempo en el archivo logtime.txt
            with open(nombre_archivo_log, "a", encoding="utf-8") as archivo:
                if cantidad_movimientos_ia == 1:
                    # Escribir información de la configuración en el primer movimiento
                    algoritmo_texto = "Alfa-Beta" if modo_busqueda_alfa_beta else "Minimax"
                    color_ia = "Negras" if jugador_usuario == logica.JUGADOR_BLANCO else "Blancas"
                    archivo.write(f"Configuración: {algoritmo_texto} | Nivel {nivel_ia_seleccionado} | IA juega con {color_ia}\n")
                    archivo.write("-" * 50 + "\n")
                
                archivo.write(f"Movimiento {cantidad_movimientos_ia}: {tiempo_movimiento:.8f} segundos\n")

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
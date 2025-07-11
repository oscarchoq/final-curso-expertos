# Documentación: Juego de Damas con Inteligencia Artificial

## Descripción General

Este proyecto implementa un juego de damas completo con una interfaz gráfica y una inteligencia artificial (IA) basada en algoritmos de búsqueda. El juego sigue las reglas tradicionales de las damas, incluyendo capturas obligatorias, capturas múltiples, y promoción a dama.

## Estructura del Proyecto

El proyecto está dividido en dos módulos principales:

1. **busqueda.py**: Implementa la lógica del juego y los algoritmos de IA
2. **juego.py**: Maneja la interfaz gráfica y la interacción con el usuario
3. **LogTime/**: Carpeta donde se almacenan los registros de tiempo de la IA

## Funcionalidades Principales

### Reglas del Juego Implementadas

- **Tablero 8x8** (configurable a otros tamaños)
- **Movimientos regulares**: Peones avanzan en diagonal, damas pueden moverse en cualquier dirección diagonal
- **Capturas obligatorias**: Si existe la posibilidad de capturar, es obligatorio hacerlo
- **Capturas múltiples**: Si después de una captura se puede realizar otra, debe continuarse
- **Coronación**: Los peones se convierten en damas al llegar a la última fila
- **Condiciones de victoria**: Capturar todas las piezas del oponente o bloquear todos sus movimientos

### Sistema de IA

La IA utiliza algoritmos avanzados para tomar decisiones:

1. **Minimax**: Algoritmo básico que evalúa posibles movimientos futuros
2. **Minimax con poda Alfa-Beta**: Versión optimizada que reduce el espacio de búsqueda

### Niveles de Dificultad

El juego implementa 5 niveles de dificultad que afectan el comportamiento de la IA:

| Nivel | Nombre | Profundidad de Búsqueda | Probabilidad de Error | Descripción |
|-------|--------|-------------------------|----------------------|-------------|
| 1 | Principiante | 1 | 30% | IA muy básica, comete errores frecuentes |
| 2 | Fácil | 2 | 20% | IA básica, algunos errores ocasionales |
| 3 | Intermedio | 3 | 10% | IA competente, pocos errores |
| 4 | Difícil | 4 | 5% | IA avanzada, muy pocos errores |
| 5 | Experto | 5 | 0% | IA máxima, juego perfecto |

### Medición de Rendimiento

El sistema registra detalladamente el rendimiento de la IA:

- **Tiempo de cálculo**: Mide el tiempo real que tarda la IA en calcular cada movimiento
- **Archivos de registro**: Genera archivos únicos por partida con formato `logtime_YYYYMMDD_HHMMSS.txt`
- **Estadísticas**: Calcula y muestra el tiempo promedio de la IA al finalizar cada partida

## Descripción Técnica de los Módulos

### Módulo `busqueda.py`

Este módulo contiene la lógica del juego y los algoritmos de IA:

#### Configuración del Juego

- Definición del tablero, piezas y reglas básicas
- Configuración de niveles de dificultad

#### Funciones del Tablero

- `tablero_inicial()`: Inicializa el tablero con la disposición estándar
- `movimientos_disponibles()`: Calcula todos los movimientos válidos para un jugador
- `aplicar_movimiento()`: Ejecuta un movimiento y actualiza el estado del tablero
- `determinar_ganador()`: Verifica si hay un ganador según las reglas

#### Funciones de IA

- `debe_cometer_error()`: Determina si la IA debe cometer un error intencional según su nivel
- `calcular_utilidad()`: Evalúa el valor heurístico de una posición del tablero
- `algoritmo_minimax()`: Implementa el algoritmo Minimax básico
- `algoritmo_minimax_alfa_beta()`: Implementa Minimax con optimización Alfa-Beta

### Módulo `juego.py`

Este módulo maneja la interfaz gráfica y la interacción del usuario:

#### Interfaz Gráfica

- Dibujo del tablero y piezas usando Pygame
- Selección de piezas y visualización de movimientos
- Visualización de información de nivel y estadísticas

#### Interacción del Usuario

- Selección de nivel de dificultad
- Selección de color de jugador
- Sistema de turnos y control del juego

#### Registro de Tiempos

- Medición precisa del tiempo de cálculo de la IA
- Generación de archivos de registro con estadísticas
- Visualización de resumen al finalizar la partida

## Algoritmos Principales

### Algoritmo Minimax

El algoritmo Minimax es una técnica de búsqueda recursiva que simula los posibles movimientos futuros:

1. Construye un árbol de jugadas posibles hasta una profundidad determinada
2. Evalúa la "utilidad" de cada posición final
3. Asume que el oponente siempre hará el mejor movimiento posible
4. Selecciona el movimiento que maximiza la utilidad mínima garantizada

### Poda Alfa-Beta

La poda Alfa-Beta es una optimización del algoritmo Minimax:

1. Mantiene dos valores: alfa (mejor valor para MAX) y beta (mejor valor para MIN)
2. Si un movimiento es peor que lo ya encontrado, ese camino se "poda" (no se explora más)
3. Reduce significativamente el espacio de búsqueda sin afectar el resultado final

### Función de Evaluación

La función `calcular_utilidad()` evalúa una posición del tablero considerando:

1. Cantidad de piezas de cada jugador
2. Valor especial para las damas (más alto que los peones)
3. Posición de las piezas en el tablero (avance, cercanía al centro)
4. Movilidad (cantidad de movimientos disponibles)

## Mejoras y Características Avanzadas

1. **Capturas múltiples obligatorias**: El jugador debe continuar capturando si es posible
2. **Medición de tiempo real**: Se registra con precisión el tiempo de cálculo de la IA
3. **Archivos de log únicos**: Se genera un archivo por partida con nombre basado en fecha y hora
4. **Visualización de estadísticas**: Muestra el tiempo promedio de la IA al finalizar la partida
5. **Algoritmos optimizados**: Implementación eficiente de Minimax con poda Alfa-Beta

## Cómo Ejecutar el Juego

1. Asegúrate de tener Python y Pygame instalados
2. Ejecuta `python juego.py` desde la terminal
3. Selecciona el nivel de dificultad y tu color (blancas o negras)
4. ¡Disfruta del juego!

## Desarrollos Futuros Posibles

1. Implementación de apertura de libros para mejorar la estrategia inicial
2. Aprendizaje automático para mejorar la IA con el tiempo
3. Multijugador en red para jugar contra otros jugadores
4. Análisis de partidas con recomendaciones de mejora

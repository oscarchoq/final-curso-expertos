# Documentación: Juego de Damas con Inteligencia Artificial (Optimizado)

## Descripción General

Este proyecto implementa un juego de damas completo con una interfaz gráfica y una inteligencia artificial (IA) basada en algoritmos de búsqueda. El juego sigue las reglas tradicionales de las damas, incluyendo capturas obligatorias y promoción a dama. **El código ha sido completamente optimizado** eliminando funcionalidades innecesarias y simplificando la arquitectura.

## Estructura del Proyecto (Optimizada)

El proyecto está dividido en módulos especializados con arquitectura orientada a objetos:

1. **main.py**: Clase principal `JuegoDamas` que controla toda la aplicación
2. **configuracion.py**: Constantes y configuraciones centralizadas
3. **tablero.py**: Lógica del tablero y validación de reglas
4. **jugador.py**: Clases de jugadores simplificadas
5. **algoritmos.py**: Algoritmos de IA optimizados
6. **LogTime/**: Carpeta donde se almacenan los registros de tiempo de la IA

## Funcionalidades Principales

### Reglas del Juego Implementadas

- **Tablero 8x8** (configurable desde configuracion.py)
- **Movimientos regulares**: Peones avanzan en diagonal, damas pueden moverse en cualquier dirección diagonal
- **Capturas obligatorias**: Si existe la posibilidad de capturar, es obligatorio hacerlo
- **Coronación**: Los peones se convierten en damas al llegar a la última fila
- **Condiciones de victoria**: Capturar todas las piezas del oponente o bloquear todos sus movimientos

### Sistema de IA Optimizado

La IA utiliza algoritmos avanzados para tomar decisiones:

1. **Minimax**: Algoritmo básico que evalúa posibles movimientos futuros
2. **Minimax con poda Alfa-Beta**: Versión optimizada que reduce el espacio de búsqueda

### Niveles de Dificultad (Optimizado a 3 niveles)

El juego implementa **3 niveles de dificultad optimizados** que ofrecen experiencia balanceada:

| Nivel | Nombre | Profundidad de Búsqueda | Probabilidad de Error | Descripción |
|-------|--------|-------------------------|----------------------|-------------|
| 1 | Principiante | 1 | 30% | IA básica, comete errores frecuentes para principiantes |
| 2 | Intermedio | 3 | 10% | IA competente, pocos errores, juego equilibrado |
| 3 | Experto | 5 | 0% | IA máxima, juego perfecto, máximo desafío |

### Medición de Rendimiento

El sistema registra detalladamente el rendimiento de la IA:

- **Tiempo de cálculo**: Mide el tiempo real que tarda la IA en calcular cada movimiento
- **Archivos de registro**: Genera archivos únicos por partida con formato `logtime_YYYYMMDD_HHMMSS.txt`
- **Estadísticas**: Calcula y muestra el tiempo promedio de la IA al finalizar cada partida

## Descripción Técnica de los Módulos (Arquitectura Optimizada)

### Módulo `main.py` (Clase Principal)

Este módulo contiene la clase principal que gestiona todo el juego:

#### Clase `JuegoDamas`

- **Gestión de interfaz**: Control completo de la interfaz gráfica con pygame
- **Control de estados**: Manejo de configuración inicial, juego y pantalla final
- **Coordinación de jugadores**: Interacción entre jugador humano e IA
- **Sistema de logging**: Registro automático de tiempos de IA

### Módulo `configuracion.py`

Centraliza todas las constantes y configuraciones:

- **Constantes del tablero**: Dimensiones, tipos de piezas, valores
- **Configuración de IA**: Niveles de dificultad optimizados (3 niveles)
- **Constantes de interfaz**: Colores, dimensiones de ventana
- **Sistema de errores**: Probabilidades por nivel

### Módulo `tablero.py`

Gestiona el estado del tablero y reglas del juego:

#### Clase `Tablero`

- `inicializar_tablero()`: Configuración inicial del tablero
- `movimientos_disponibles()`: Calcula todos los movimientos válidos para un jugador
- `aplicar_movimiento()`: Ejecuta un movimiento y retorna nuevo estado del tablero
- `es_final()`: Verifica si hay movimientos disponibles
- `determinar_ganador()`: Determina el ganador según las reglas

### Módulo `jugador.py` (Simplificado)

Clases optimizadas para manejar jugadores:

#### Clases Principales

- `Jugador`: Clase base abstracta
- `JugadorHumano`: Maneja interacción básica del usuario (simplificado)
- `GestorMovimientos`: Coordina movimientos y validaciones básicas

### Módulo `algoritmos.py` (Optimizado)

Implementación completa de algoritmos de IA:

#### Clases Principales

- `ConfiguracionIA`: Gestiona configuración de dificultad
- `EvaluadorTablero`: Implementa función de evaluación heurística optimizada
- `AlgoritmoMinimax`: Algoritmo Minimax básico
- `AlgoritmoMinimaxAlfaBeta`: Minimax con poda Alfa-Beta
- `JugadorIA`: Orquesta todos los algoritmos

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

### Función de Evaluación Optimizada

La función `calcular_utilidad()` evalúa una posición del tablero considerando:

1. **Cantidad de piezas**: Puntaje base por número de piezas
2. **Valor de damas**: Las damas tienen mayor valor que los peones
3. **Posición estratégica**: Bonificación por avance hacia coronación
4. **Control del centro**: Valoración de piezas en posiciones centrales

## Optimizaciones Realizadas

### ✅ Eliminaciones de Código Innecesario

1. **Sistema de capturas consecutivas**: Removido completamente para simplificar el juego
2. **Imports no utilizados**: Limpieza de todas las importaciones innecesarias
3. **Variables no utilizadas**: Eliminación de variables y métodos sin uso
4. **Comentarios redundantes**: Optimización de documentación

### ✅ Simplificaciones Arquitectónicas

1. **Reducción de niveles**: De 5 a 3 niveles de dificultad optimizados
2. **Interfaz simplificada**: Botones y controles más directos
3. **Clases simplificadas**: Eliminación de funcionalidades complejas innecesarias
4. **Flujo de juego directo**: Menos estados intermedios, más fluido

### ✅ Mejoras de Rendimiento

1. **Algoritmos optimizados**: Implementación más eficiente
2. **Memoria optimizada**: Mejor gestión de recursos
3. **Código más limpio**: Mayor velocidad de ejecución
4. **Debugging simplificado**: Menos puntos de fallo

## Cómo Ejecutar el Juego

1. Asegúrate de tener Python y Pygame instalados
2. Ejecuta `python main.py` desde la terminal
3. Selecciona el nivel de dificultad y tu color (blancas o negras)
4. ¡Disfruta del juego optimizado!

## Estado Actual del Proyecto

### ✅ Completamente Funcional
- Arquitectura orientada a objetos optimizada
- 3 niveles de dificultad balanceados
- Interfaz gráfica moderna y fluida
- Sistema de logging de rendimiento
- Código limpio sin funcionalidades innecesarias

### ✅ Validaciones Completas
- Movimientos válidos según reglas de damas
- Capturas obligatorias implementadas
- Promoción automática a dama
- Detección de fin de juego

### ✅ Optimizaciones Implementadas
- Eliminación de código innecesario
- Limpieza de imports y variables
- Comentarios optimizados
- Arquitectura simplificada y eficiente

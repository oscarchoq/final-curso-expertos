# Juego de Damas con Inteligencia Artificial 🎯

Un juego de damas implementado en Python con arquitectura orientada a objetos y algoritmos avanzados de inteligencia artificial.

## ✨ Características Principales

- **Arquitectura Orientada a Objetos**: Diseño modular y profesional
- **Interfaz Gráfica Moderna**: Implementada con pygame
- **IA Avanzada**: 3 niveles de dificultad optimizados (Principiante, Intermedio, Experto)
- **Algoritmos Implementados**: Minimax y Minimax con poda Alfa-Beta
- **Validación Completa**: Movimientos, capturas múltiples y reglas oficiales
- **Sistema de Promoción**: Transformación automática a reinas
- **Sistema de Errores Probabilísticos**: IA con comportamiento realista según el nivel

## 🛠️ Requisitos del Sistema

- **Python**: 3.8 o superior
- **Pygame**: Para la interfaz gráfica
- **Sistema Operativo**: Windows, macOS, Linux

## 📦 Instalación

```bash
# Instalar pygame
pip install pygame

# Ejecutar el juego
python main.py
```

## 🚀 Formas de Ejecutar

### Versión Principal

```bash
# Ejecutar el juego
python main.py
```

## 📁 Estructura del Proyecto

```
Final-Curso/
├── 🎮 main.py               # Archivo principal - Arquitectura OOP
├── 🎯 configuracion.py      # Constantes y configuraciones
├── 🏁 tablero.py           # Lógica del tablero y reglas
├── 👤 jugador.py           # Clases de jugadores (Humano/IA)
├── 🧠 algoritmos.py        # Algoritmos de inteligencia artificial
└── 🎵 OpenSans-Regular.ttf # Fuente para la interfaz
```

## 🧠 Algoritmos de Inteligencia Artificial

### 🎯 Minimax Básico
- **Descripción**: Algoritmo de búsqueda que explora todas las posibilidades
- **Profundidad**: Configurable según el nivel
- **Uso**: Niveles básicos de dificultad

### ⚡ Minimax con Poda Alfa-Beta
- **Descripción**: Versión optimizada que elimina ramas innecesarias
- **Eficiencia**: Hasta 10x más rápido que minimax básico
- **Uso**: Niveles avanzados de dificultad

## 🎚️ Niveles de Dificultad

| Nivel | Nombre | Profundidad | Algoritmo | Error Prob. | Características |
|-------|--------|-------------|-----------|-------------|-----------------|
| 1 | Principiante | 1 | Minimax | 30% | Movimientos básicos, errores frecuentes |
| 2 | Intermedio | 3 | Alfa-Beta | 10% | Evaluación completa, pocos errores |
| 3 | Experto | 5 | Alfa-Beta | 0% | Estrategia perfecta, nivel máximo |

## 🎮 Controles del Juego

- **Seleccionar pieza**: Clic izquierdo en tu pieza
- **Mover**: Clic izquierdo en casilla válida destacada
- **Configuración inicial**: Selecciona color y nivel de IA

## 🏆 Características Técnicas

### ✅ Validaciones Implementadas

- Movimientos diagonales únicos
- Capturas obligatorias cuando están disponibles
- Capturas múltiples en secuencia
- Promoción automática al alcanzar el extremo opuesto
- Detección de fin de juego

### 🚀 Optimizaciones de Rendimiento

- Poda Alfa-Beta para reducir espacio de búsqueda
- Evaluación heurística optimizada
- Manejo eficiente de memoria
- Sistema de errores probabilísticos para realismo

## 🔧 Arquitectura del Software

### 🏗️ Diseño Orientado a Objetos

```python
JuegoDamas (Clase Principal)
├── Tablero (Estado del juego)
├── JugadorIA (Inteligencia artificial)
├── JugadorHumano (Interacción usuario)
└── Configuracion (Constantes y settings)
```

## 📚 Documentación Adicional

- [📋 REFACTORIZACION.md](REFACTORIZACION.md) - Detalles del proceso de refactorización
- [📚 DOCUMENTACION.md](DOCUMENTACION.md) - Documentación técnica completa

---

## Desarrollo

Desarrollado con ❤️ usando Python y arquitectura orientada a objetos

## Estado Actual del Proyecto

- ✅ Sistema de 3 niveles de dificultad optimizado
- ✅ Algoritmos Minimax y Alfa-Beta implementados
- ✅ Sistema de errores probabilísticos para IA realista
- ✅ Interfaz gráfica moderna con pygame
- ✅ Arquitectura orientada a objetos completa
- ✅ Validaciones completas de reglas de damas

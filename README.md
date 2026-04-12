# Pacman AI — Poda Alfa-Beta y Búsqueda Competitiva

**Hernández Prado Osmar Javier** | 2do Parcial — Inteligencia Artificial

## Descripción

Simulación del clásico juego Pacman desarrollada en Python con renderizado 3D mediante OpenGL/PyOpenGL y gestión de ventana/audio con PyGame. El proyecto implementa cuatro agentes fantasma con distintos niveles de inteligencia, desde movimiento puramente aleatorio hasta búsqueda competitiva colaborativa con Poda Alfa-Beta.

## Estructura del Proyecto

```
/
├── main.py          # Incluye el punto principal, estados del juego, cámara, audio
├── Ghost.py         # Clase Ghost: todos los agentes y algoritmos de IA
├── Pacman.py        # Clase Pacman: movimiento del jugador + input buffer
├── mapa.bmp         # Textura del laberinto
├── mapa.csv         # Matriz de control del laberinto
├── pacman.bmp       # Textura de Pacman
├── fantasma1.bmp    # Textura Clyde (naranja)
├── fantasma2.bmp    # Textura Inky (azul)
├── fantasma3.bmp    # Textura Pinky (rosa)
└── fantasma4.bmp    # Textura Blinky (rojo)
```

## Agentes Implementados (Requisitos del Examen)

### Blinky — Rojo (Tipo 0) · Pregunta 1

Agente de control con movimiento aleatorio. Solo toma decisiones en intersecciones válidas de la Matriz de Control y nunca regresa por el camino de llegada (`interseccion_random()`).

### Pinky — Rosa (Tipo 1) · Pregunta 2

Agente racional con Minimax + Poda Alfa-Beta (profundidad 3). Su función de evaluación combina dos componentes heurísticos:

- **Distancia Manhattan (peso 0.75):** domina porque el laberinto no permite movimiento diagonal.
- **Distancia Euclidiana (peso 0.25):** desempate geométrico cuando dos rutas tienen igual distancia Manhattan.

### Inky y Clyde — Cian/Naranja (Tipo 2) · Pregunta 3

Agentes colaborativos con Alfa-Beta y heurística de caza en manada (`heuristica_colaborativa()`). Dos componentes heurísticos:

- **Distancia al Pacman:** objetivo principal compartido.
- **Bonus de separación por eje:** cuando los dos fantasmas están a menos de 5 celdas entre sí, Clyde prioriza separación horizontal e Inky separación vertical, evitando la aglomeración y forzando un cerco desde ángulos distintos.

### Motor Alfa-Beta con Mejoras · Pregunta 4

Dos estrategias de mejora integradas en `alfa_beta()`:

- **Búsqueda Tabú (horizonte limitado):** durante la simulación interna, si un movimiento lleva a una celda ya visitada en esa rama (`nueva_lista_tabu`), la poda. Esto elimina ciclos inútiles sin memoria global entre turnos.
- **Búsqueda en Reposo (continuación heurística):** si al llegar a profundidad 0 el fantasma está a ≤ 2 celdas del Pacman, el horizonte se extiende hasta 2 niveles extra (`profundidad_reposo < 2`) para no tomar decisiones ciegas en el momento crítico.

## Extras Implementados

### Input Buffer (`Pacman.py`)

Ventana de 200 ms (`BUFFER_WINDOW = 0.20`) que guarda el último input del jugador. Si Pacman llega a la siguiente intersección dentro de ese tiempo, ejecuta el giro aunque ya no se esté presionando la tecla. Esto elimina el "input perdido" en el control de cuadrícula.

### Secuencia de Inicio (`main.py`)

El juego arranca con una secuencia de 4 estados:

1. **Intro** (3 s): animación de cámara con interpolación cúbica (`ease_out_cubic`) desde vista lejana hasta vista de juego.
2. **LISTO?** (1.5 s): texto en pantalla con parpadeo senoidal.
3. **VAMOS!** (0.8 s): texto con fade-out y escala creciente.
4. **Juego**: loop normal.

### Sonido de Inicio Generado por Código

El sonido de inicio se genera en tiempo de ejecución con numpy — una secuencia de notas con envolvente exponencial, sin archivos de audio externos.

### Detección de Captura con Log en Consola

Cuando un fantasma toca a Pacman, se imprime en consola el nombre del fantasma, su tipo de comportamiento y el conteo acumulado de capturas. El fantasma se congela mientras sigue en contacto.

## Requisitos

- Python 3.10 (recomendado para compatibilidad con PyOpenGL)
- PyGame, PyOpenGL, numpy, pandas

## Instalación

```bash
# Con conda (recomendado)
conda create --name pacman_ia python=3.10
conda activate pacman_ia
pip install pygame PyOpenGL numpy pandas

# Con venv
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/Mac
pip install pygame PyOpenGL numpy pandas
```

## Ejecución

```bash
python main.py
```

**Controles:** `W` `A` `S` `D` — mover Pacman | `ESC` — salir.
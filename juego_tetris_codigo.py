import pygame
import random

# --- Configuración básica ---
ANCHO_TABLERO = 10
ALTO_TABLERO = 20
TAM_CELDA = 30

ANCHO_VENTANA = ANCHO_TABLERO * TAM_CELDA
ALTO_VENTANA = ALTO_TABLERO * TAM_CELDA

# Tiempo (ms) entre caídas automáticas
TIEMPO_CAIDA = 500

PIEZAS = {
    'I': [
        ["....",
         "####",
         "....",
         "...."],
    ],
    'O': [
        ["....",
         ".##.",
         ".##.",
         "...."],
    ],
    'T': [
        ["....",
         ".###",
         "..#.",
         "...."],
    ],
    'L': [
        ["....",
         ".#..",
         ".###",
         "...."],
    ],
    'J': [
        ["....",
         "...#",
         ".###",
         "...."],
    ],
    'S': [
        ["....",
         "..##",
         ".##.",
         "...."],
    ],
    'Z': [
        ["....",
         ".##.",
         "..##",
         "...."],
    ],
}

COLORES = {
    'I': (0, 255, 255),
    'O': (255, 255, 0),
    'T': (160, 0, 240),
    'L': (255, 165, 0),
    'J': (0, 0, 255),
    'S': (0, 255, 0),
    'Z': (255, 0, 0),
}

def crear_tablero():
    return [[0 for _ in range(ANCHO_TABLERO)] for _ in range(ALTO_TABLERO)]

def nueva_pieza():
    tipo = random.choice(list(PIEZAS.keys()))
    forma = PIEZAS[tipo][0]
    x = ANCHO_TABLERO // 2 - 2
    y = 0
    return {'x': x, 'y': y, 'forma': forma, 'tipo': tipo}

def colision(pieza, tablero, dx=0, dy=0):
    forma = pieza['forma']
    x0 = pieza['x'] + dx
    y0 = pieza['y'] + dy

    for fila in range(4):
        for col in range(4):
            if forma[fila][col] == '#':
                x = x0 + col
                y = y0 + fila

                if x < 0 or x >= ANCHO_TABLERO or y >= ALTO_TABLERO:
                    return True

                if y >= 0 and tablero[y][x] != 0:
                    return True
    return False

def fijar_pieza(pieza, tablero):
    forma = pieza['forma']
    color = COLORES[pieza['tipo']]
    for fila in range(4):
        for col in range(4):
            if forma[fila][col] == '#':
                x = pieza['x'] + col
                y = pieza['y'] + fila
                if 0 <= y < ALTO_TABLERO:
                    tablero[y][x] = color

def borrar_lineas(tablero):
    nuevas_filas = []
    lineas_borradas = 0

    for fila in tablero:
        if all(celda != 0 for celda in fila):
            lineas_borradas += 1
        else:
            nuevas_filas.append(fila)

    while len(nuevas_filas) < ALTO_TABLERO:
        nuevas_filas.insert(0, [0 for _ in range(ANCHO_TABLERO)])

    return nuevas_filas, lineas_borradas

def dibujar_tablero(screen, tablero):
    for y in range(ALTO_TABLERO):
        for x in range(ANCHO_TABLERO):
            valor = tablero[y][x]
            rect = (x * TAM_CELDA, y * TAM_CELDA, TAM_CELDA, TAM_CELDA)

            color = (0, 0, 0)
            if valor != 0:
                color = valor

            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (40, 40, 40), rect, 1)

def dibujar_pieza(screen, pieza):
    forma = pieza['forma']
    color = COLORES[pieza['tipo']]
    for fila in range(4):
        for col in range(4):
            if forma[fila][col] == '#':
                x = pieza['x'] + col
                y = pieza['y'] + fila
                if y >= 0:
                    rect = (x * TAM_CELDA, y * TAM_CELDA, TAM_CELDA, TAM_CELDA)
                    pygame.draw.rect(screen, color, rect)
                    pygame.draw.rect(screen, (40, 40, 40), rect, 1)

def rotar_pieza(pieza):
    # rotación simple 90° (transponer + invertir filas)
    forma = pieza['forma']
    nueva = ["".join(forma[3 - j][i] for j in range(4)) for i in range(4)]
    return nueva

def main():
    pygame.init()
    screen = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
    pygame.display.set_caption("Tetris básico")
    clock = pygame.time.Clock()

    tablero = crear_tablero()
    pieza = nueva_pieza()
    tiempo_acumulado = 0
    puntos = 0

    fuente = pygame.font.SysFont("Arial", 20)

    running = True
    while running:
        dt = clock.tick(60)  # ms desde el último frame
        tiempo_acumulado += dt

        # --- Manejo de eventos ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if not colision(pieza, tablero, dx=-1, dy=0):
                        pieza['x'] -= 1
                elif event.key == pygame.K_RIGHT:
                    if not colision(pieza, tablero, dx=1, dy=0):
                        pieza['x'] += 1
                elif event.key == pygame.K_DOWN:
                    if not colision(pieza, tablero, dy=1):
                        pieza['y'] += 1
                elif event.key == pygame.K_UP:
                    # intentar rotar
                    forma_rotada = rotar_pieza(pieza)
                    original = pieza['forma']
                    pieza['forma'] = forma_rotada
                    if colision(pieza, tablero):
                        pieza['forma'] = original  # deshacer si choca

        # --- Caída automática ---
        if tiempo_acumulado >= TIEMPO_CAIDA:
            tiempo_acumulado = 0
            if not colision(pieza, tablero, dy=1):
                pieza['y'] += 1
            else:
                # fijar pieza
                fijar_pieza(pieza, tablero)
                tablero, lineas = borrar_lineas(tablero)
                puntos += lineas * 100

                # nueva pieza
                pieza = nueva_pieza()
                if colision(pieza, tablero):
                    # Game over
                    running = False

        # --- Dibujar ---
        screen.fill((0, 0, 0))
        dibujar_tablero(screen, tablero)
        dibujar_pieza(screen, pieza)

        texto = fuente.render(f"Puntos: {puntos}", True, (255, 255, 255))
        screen.blit(texto, (5, 5))

        pygame.display.flip()

    # Pantalla final simple
    screen.fill((0, 0, 0))
    texto = fuente.render("Game Over", True, (255, 0, 0))
    screen.blit(texto, (ANCHO_VENTANA // 2 - 50, ALTO_VENTANA // 2))
    pygame.display.flip()
    pygame.time.wait(2000)

    pygame.quit()

if __name__ == "__main__":
    main()

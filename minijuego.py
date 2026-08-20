"""
minijuego.py
Pequeño minijuego tipo "runner" (estilo Mario lateral): el personaje corre
solo y recolecta monedas saltando con ESPACIO. Devuelve la cantidad de
monedas recolectadas, que se convierten en puntos.

- ESPACIO: saltar
- Flecha abajo: agacharse (opcional, esquivar)
- Dura aproximadamente SOBREVIVE_T segundos.

Devuelve (monedas, puntos):  puntos = monedas * MULT (ver ruleta_core).
"""

import random
import pygame

import ruleta_core as core

SURVIVE_T = 15.0  # segundos de duracion

# colores
SKY = (135, 206, 235)
GRASS = (58, 160, 70)
GROUND_H = 24
COIN_C = (255, 215, 0)


class Objeto:
    def __init__(self, x, y, w, h, es_moneda):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.es_moneda = es_moneda
        self.recogida = False


def generar_monedas(W):
    """Genera una fila de monedas/obstaculos espaciados."""
    y = 120
    return [Objeto(x, y, 22, 22, True) for x in range(320, W + 100, 90)]


def crear_obstaculos(W, rng):
    obs = []
    x = 380
    while x < W + 120:
        if rng.random() < 0.45:
            obs.append(Objeto(x, 130, 50, 55, False))
        x += rng.randint(240, 380)
    return obs


def jugar(screen, base_y):
    """Corre la pantalla del minijuego. Devuelve (monedas, puntos)."""
    rng = random.Random()
    font = pygame.font.SysFont("Arial", 26, bold=True)
    W, H = screen.get_size()

    clock = pygame.time.Clock()
    t0 = pygame.time.get_ticks()

    # jugador
    px = 120
    pw, ph = 40, 55
    py = base_y
    vy = 0.0
    en_suelo = True
    agachado = False

    monedas = generar_monedas(W)
    monedas_proc = [m for m in monedas] + [Objeto(x, 130, 50, 55, False)
                                           for x in range(700, W + 200, 300)]
    recogidas = 0
    velocidad = 7.0

    while True:
        dt = clock.tick(60) / 1000.0
        t = (pygame.time.get_ticks() - t0) / 1000.0

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_SPACE] and en_suelo:
            vy = -13.0
            en_suelo = False
        agachado = teclas[pygame.K_DOWN]

        # fisica jugador
        if not en_suelo:
            vy += 0.9
            py += vy
            if py >= base_y:
                py = base_y
                vy = 0
                en_suelo = True
        if agachado:
            ph_a = 30
        else:
            ph_a = 55

        # mover mundo
        for ob in monedas_proc:
            ob.x -= velocidad
        monedas_proc = [ob for ob in monedas_proc if ob.x > -ob.w]

        # checkeos
        for ob in monedas_proc:
            if ob.es_moneda and not ob.recogida:
                if (px + pw - 10 > ob.x and px < ob.x + ob.w
                        and py + 10 < ob.y + ob.h and py + ph_a > ob.y):
                    ob.recogida = True
                    recogidas += 1
            elif not ob.es_moneda:
                if (px + pw > ob.x and px < ob.x + ob.w
                        and py + ph_a > ob.y and py < ob.y + ob.h):
                    # choque -> se pierde 3 monedas
                    recogidas = max(0, recogidas - 3)
                    ob.x = -200  # retira

        # fondo
        screen.fill(SKY)
        pygame.draw.rect(screen, GRASS, (0, base_y, W, base_y))
        pygame.draw.rect(screen, (130, 110, 90),
                         (0, base_y + 2, W, H - base_y))

        # jugador
        cuerpo = pygame.Rect(px, py - ph_a, pw, ph_a)
        pygame.draw.rect(screen, (255, 90, 90), cuerpo)
        pygame.draw.rect(screen, (255, 220, 180),
                         (px + 8, cuerpo.y - 12, 24, 18))
        # ojos
        pygame.draw.circle(screen, (20, 20, 20), (px + 28, cuerpo.y - 4), 3)

        # dibujar objetos
        for ob in monedas_proc:
            if ob.es_moneda and not ob.recogida:
                pygame.draw.circle(screen, COIN_C, (ob.x + 11, ob.y + 11), 10)
                pygame.draw.circle(screen, (200, 160, 0),
                                   (ob.x + 11, ob.y + 11), 6)
            elif not ob.es_moneda:
                pygame.draw.rect(screen, (120, 80, 40),
                                 (ob.x, ob.y, ob.w, ob.h))
                pygame.draw.rect(screen, (180, 130, 60),
                                 (ob.x, ob.y, ob.w, ob.h - 8))

        # hud
        tiempo = max(0.0, SURVIVE_T - t)
        screen.blit(font.render(f"Monedas: {recogidas}", True, (255, 255, 255)),
                    (20, 20))
        screen.blit(font.render(f"Tiempo: {tiempo:.1f}s", True, (255, 255, 255)),
                    (20, 55))
        screen.blit(font.render("ESPACIO salta  |  collecta monedas", True,
                                (255, 255, 255)), (20, H - 40))

        pygame.display.flip()

        if t >= SURVIVE_T:
            break

    puntos = recogidas * core.MINIJUEGO_MULT
    return recogidas, puntos
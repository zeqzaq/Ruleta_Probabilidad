"""
ruleta.py
Juego de la ruleta con pygame. 3 tiros, casillas con puntos y combos (^),
'Perdio', y un minijuego de recolectar monedas.

Controles:
    ESPACIO  -> girar la ruleta / avanzar despues del resultado
    R        -> reiniciar partida
"""

import math
import random
import pygame

import ruleta_core as core
import minijuego


# ----------------------------------------------------------------------------
# config visual
# ----------------------------------------------------------------------------
W, H = 900, 700
CX, CY = 300, 320
RADIO = 250
N = len(core.TABLERO)
ANG = 2 * math.pi / N
FPS = 60

FONDO = (24, 26, 33)
BORDE = (255, 215, 0)
COLOR_NEG = (200, 60, 60)
COLOR_POS = (60, 170, 90)
COLOR_COMBO = (240, 200, 60)
COLOR_PERDIO = (40, 40, 45)
COLOR_MINI = (150, 90, 220)
COLOR_50 = (110, 190, 220)

COLOR_TEXTO = (240, 240, 240)


def color_casilla(cas):
    tipo, valor, combo = cas
    if tipo == 'perdio':
        return COLOR_PERDIO
    if tipo == 'minijuego':
        return COLOR_MINI
    if combo:
        return COLOR_COMBO
    if valor < 0:
        return COLOR_NEG
    if valor <= 50:
        return COLOR_50
    return COLOR_POS


def val_texto(cas):
    tipo, valor, combo = cas
    if tipo == 'perdio':
        return "PERDIO"
    if tipo == 'minijuego':
        return "MINI" + ("+" if valor == 0 else "-")
    s = f"{valor:+}"
    if combo:
        s += "^"
    return s


class Ruleta:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("Arial", 22, bold=True)
        self.font_g = pygame.font.SysFont("Arial", 30, bold=True)
        self.font_m = pygame.font.SysFont("Arial", 40, bold=True)

        self.ang_ruleta = 0.0
        self.vel = 0.0
        self.girando = False
        self.esperando = False
        self.resultado = None  # casilla resuelta
        self.msg = ""
        self.estado = "jugar"  # jugar | minigame | perdio | ganar

        self.reset()

    # ------------------------------------------------------------------
    def reset(self):
        self.total = 0
        self.tiros_usados = 0
        self.historial = []
        self.estado = "jugar"
        self.msg = "Pulsa ESPACIO para girar"
        self.ultimo_texto = ""

    # ------------------------------------------------------------------
    def girar(self):
        if self.girando or self.esperando or self.estado != "jugar":
            return
        if self.tiros_usados >= core.TIROS:
            return
        self.vel = random.uniform(20, 28)
        self.girando = True
        self.resultado = None
        self.msg = "Girando..."

    # ------------------------------------------------------------------
    def _indice_casilla(self):
        # el puntero mira hacia el topo de la ruleta (12h), que en las
        # coordenadas de dibujo corresponde al angulo -90° (arriba).
        topo = -math.pi / 2
        rel = (topo - self.ang_ruleta) % (2 * math.pi)
        return int(rel / ANG) % N

    def _casilla_current(self):
        return core.TABLERO[self._indice_casilla()]

    def _avanzar(self):
        """Aplica el resultado detenido y pasa al siguiente paso."""
        cas = self.resultado
        tipo, valor, combo = cas
        self.historial.append((tipo, valor, combo))

        if tipo == 'perdio':
            self.total = 0
            self.estado = "perdio"
            self.msg = "PERDISTE TODO (casilla Perdio). Pulsa R"
            self.ultimo_texto = "PERDIO"
            return

        if tipo == 'minijuego':
            self.estado = "minigame"
            signo = "suma" if valor == 0 else "resta"
            self.msg = f"Minijuego ({signo})! Pulsa ESPACIO para jugarlo"
            self.ultimo_texto = f"MINI ({signo})"
            return

        self.total += valor
        self.ultimo_texto = f"{valor:+}{'^' if combo else ''}"

        if combo:
            self.msg = f"COMBO {valor:+}! No gastas tiro. Pulsa ESPACIO"
            self.estado = "jugar"
            self.tiros_usados += 0
        else:
            self.tiros_usados += 1
            self.msg = f"{valor:+} puntos. Pulsa ESPACIO"

        if self.total >= core.META:
            self.estado = "ganar"
            self.msg = "GANASTE! >= 1500 puntos. Pulsa R"
        elif self.tiros_usados >= core.TIROS:
            if self.total >= core.META:
                self.estado = "ganar"
                self.msg = "GANASTE! >= 1500 puntos. Pulsa R"
            else:
                self.estado = "perdio"
                self.msg = f"Se acabaron los tiros: {self.total} pts. Pulsa R"

    # ------------------------------------------------------------------
    def _terminar_minigame(self, pts):
        self.total += pts
        self.ultimo_texto = f"MINI: {pts:+}"
        self.tiros_usados += 1
        if self.total >= core.META:
            self.estado = "ganar"
            self.msg = "GANASTE! Pulsa R"
        elif self.tiros_usados >= core.TIROS:
            self.estado = "perdio"
            self.msg = f"Se acabaron los tiros: {self.total} pts. Pulsa R"
        else:
            self.estado = "jugar"
            self.msg = f"Minijuego: {pts:+}. Total {self.total}. Pulsa ESPACIO"

    # ------------------------------------------------------------------
    def update(self):
        if self.girando:
            self.ang_ruleta += self.vel * 0.0166
            self.vel *= 0.965
            if self.vel < 0.15:
                self.vel = 0
                self.girando = False
                self.esperando = True
                self.resultado = self._casilla_current()
                self.msg = "Se detuvo aqui. Pulsa ESPACIO"

    # ------------------------------------------------------------------
    def manejar_evento(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_r:
                self.reset()
            elif e.key == pygame.K_SPACE:
                if self.esperando and self.resultado is not None:
                    self.esperando = False
                    self._avanzar()
                elif self.estado == "minigame":
                    coins, pts = minijuego.jugar(self.screen, 560)
                    self._terminar_minigame(pts)
                else:
                    self.girar()

    # ------------------------------------------------------------------
    def _dibujar_ruleta(self):
        for i in range(N):
            a0 = self.ang_ruleta + i * ANG
            a1 = a0 + ANG
            cas = core.TABLERO[i]
            col = color_casilla(cas)
            poly = [(CX, CY)]
            for k in range(30):
                a = a0 + (a1 - a0) * (k / 29.0)
                poly.append((CX + RADIO * math.cos(a), CY + RADIO * math.sin(a)))
            pygame.draw.polygon(self.screen, col, poly)

            # texto rotado
            am = a0 + ANG / 2
            rx, ry = CX + (RADIO * 0.74) * math.cos(am), CY + (RADIO * 0.74) * math.sin(am)
            txt = val_texto(cas)
            surf = self.font.render(txt, True, (20, 20, 20))
            surf = pygame.transform.rotate(surf, -math.degrees(am))
            rect = surf.get_rect(center=(rx, ry))
            self.screen.blit(surf, rect)

        # borde
        pygame.draw.circle(self.screen, BORDE, (CX, CY), RADIO + 6, 6)
        pygame.draw.circle(self.screen, (60, 60, 70), (CX, CY), 40)

    def _dibujar_ojos(self):
        pygame.draw.circle(self.screen, (255, 255, 255), (CX - 10, CY), 13)
        pygame.draw.circle(self.screen, (255, 255, 255), (CX + 10, CY), 13)
        pygame.draw.circle(self.screen, (20, 20, 20), (CX - 7, CY), 6)
        pygame.draw.circle(self.screen, (20, 20, 20), (CX + 7, CY), 6)

    def _dibujar_puntero(self):
        pts = [(CX, CY - RADIO - 30), (CX - 18, CY - RADIO - 60),
               (CX + 18, CY - RADIO - 60)]
        pygame.draw.polygon(self.screen, (255, 255, 255), pts)

    # ------------------------------------------------------------------
    def _dibujar_hud(self):
        # panel derecho
        panel_x = CX + RADIO + 40
        # titulo
        t = self.font_g.render("RULETA", True, BORDE)
        self.screen.blit(t, (panel_x, 60))

        t = self.font.render(f"Total: {self.total} pts", True,
                             (100, 255, 100) if self.total >= 0 else (255, 120, 120))
        self.screen.blit(t, (panel_x, 120))
        t = self.font.render(f"Tiros usados: {self.tiros_usados}/{core.TIROS}", True, COLOR_TEXTO)
        self.screen.blit(t, (panel_x, 155))
        t = self.font.render(f"Tiros combo: {len([h for h in self.historial if h[2]])}", True, COLOR_TEXTO)
        self.screen.blit(t, (panel_x, 190))

        # ultimo resultado
        t = self.font.render(f"Ultimo: {self.ultimo_texto}", True, (240, 210, 90))
        self.screen.blit(t, (panel_x, 240))

        # mensaje principal
        lines = self.msg.split('\n')
        for i, li in enumerate(lines):
            s = self.font.render(li, True, COLOR_TEXTO)
            self.screen.blit(s, (panel_x, 300 + i * 30))

        # estado
        est = pygame.Surface((260, 60), pygame.SRCALPHA)
        if self.estado == "ganar":
            col = (60, 220, 90, 200)
        elif self.estado == "perdio":
            col = (220, 60, 60, 200)
        else:
            col = (60, 60, 70, 160)
        pygame.draw.rect(est, col, est.get_rect(), border_radius=10)
        self.screen.blit(est, (panel_x, 380))
        nom = {"jugar": "EN JUEGO", "minigame": "MINIJUEGO",
               "ganar": "GANASTE!", "perdio": "DERROTA"}[self.estado]
        c = self.font_g.render(nom, True, COLOR_TEXTO)
        self.screen.blit(c, (panel_x + 10, 395))

    # ------------------------------------------------------------------
    def run(self):
        clock = pygame.time.Clock()
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                self.manejar_evento(e)
            self.update()
            self.screen.fill(FONDO)
            self._dibujar_ruleta()
            self._dibujar_ojos()
            self._dibujar_puntero()
            self._dibujar_hud()
            pygame.display.flip()
            clock.tick(FPS)


def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Ruleta - Probabilidad y Metodos Numericos")
    r = Ruleta(screen)
    r.run()


if __name__ == "__main__":
    main()
"""
ruleta_core.py
Reglas y tablero de la ruleta. Este modulo es la fuente de verdad (single
source of truth) usada tanto por la simulacion como por el juego en pygame.

Reglas:
    - 3 tiros. Cada tiro suma o resta puntos al total acumulado.
    - Toda casilla marcada con combo ('^') aplica su valor PERO NO gasta tiro
      (puede encadenarse con mas combos o un tiro normal).
    - 'Perdio' -> la partida termina al instante con 0 puntos (derrota total).
    - 'minijuego+' / 'minijuego-' aplican puntos aleatorios segun parametros.
    - Gana quien alcanza >= META puntos al final de sus tiros.
"""

import random

# ----------------------------------------------------------------------------
# Tablero: lista de casillas. Cada elemento es (tipo, valor, combo).
#   tipo:  'pts'        -> puntos directos
#          'perdio'     -> pierde toda la partida
#          'minijuego'  -> puntos variables
#   combo: True si la casilla NO gasta tiro (^)
# ----------------------------------------------------------------------------
_TIPO = 0
_VALOR = 1
_COMBO = 2


def _build_tablero():
    """Construye la lista de 41 casillas usando las cantidades definidas."""
    t = []
    # (cantidad, valor, combillo)
    specs = [
        (1, 1000, False), (1, -1000, False),
        (3, 500, False), (3, -500, False),
        (1, 500, True), (1, -500, True),
        (4, 300, False), (4, -300, False),
        (1, 300, True), (1, -300, True),
        (5, 100, False), (5, -100, False),
        (1, 100, True), (1, -100, True),
        (6, 50, False),
    ]
    for cant, valor, combo in specs:
        for _ in range(cant):
            t.append(('pts', valor, combo))
    # casillas especiales
    t.append(('perdio', 0, False))
    t.append(('minijuego', 0, False))   # suma  -> minijuego_positivo
    t.append(('minijuego', 1, False))   # resta -> minijuego_negativo
    assert len(t) == 41, f"Se esperaban 41 casillas, hay {len(t)}"
    return _mezclar(t)


def _mezclar(casillas):
    """
    Reordena las casillas para que valores iguales NO queden contiguos y los
    signos alternen en la medida de lo posible (visual mas agradable y
    menos '100 100 100' juntos).

    Estrategia:
      1) separar en: positivas normales, negativas normales, combos, especiales.
      2) barajar cada grupo (se reparten los valores iguales).
      3) intercalar positivas/negativas.
      4) insertar combos y especiales en posiciones espaciadas.
    """
    rng = random.Random(12345)  # fijo -> orden reproducible
    pos = [c for c in casillas if c[_TIPO] == 'pts' and c[_VALOR] > 0 and not c[_COMBO]]
    neg = [c for c in casillas if c[_TIPO] == 'pts' and c[_VALOR] < 0 and not c[_COMBO]]
    comb = [c for c in casillas if c[_COMBO]]
    espec = [c for c in casillas if c[_TIPO] != 'pts']

    rng.shuffle(pos)
    rng.shuffle(neg)
    rng.shuffle(comb)
    rng.shuffle(espec)

    # 1) intercalar pos/neg para alternar signos
    base = []
    pi = ni = 0
    turno_pos = True
    while pi < len(pos) or ni < len(neg):
        if turno_pos and pi < len(pos):
            base.append(pos[pi]); pi += 1
        elif ni < len(neg):
            base.append(neg[ni]); ni += 1
        turno_pos = not turno_pos

    # 1b) excedente de positivas (las hay de sobra): en lugar de dejar un
    #     bloque al final, repartirlas intercaladas para no pegar signos iguales.
    surplus = pos[pi:]
    if surplus:
        paso_s = max(1, len(base) // (len(surplus) + 1))
        for k, c in enumerate(surplus):
            idx = min(len(base), (k + 1) * paso_s)
            base.insert(idx, c)

    # 2) distribuir combos cada ~7 posiciones y especiales repartidos
    paso = max(1, len(base) // (len(comb) + 1))
    for k, c in enumerate(comb):
        idx = min(len(base), (k + 1) * paso)
        base.insert(idx, c)

    # especiales separados unos de otros
    paso_e = max(1, len(base) // (len(espec) + 1))
    for k, s in enumerate(espec):
        idx = min(len(base), (k + 1) * paso_e)
        base.insert(idx, s)

    assert len(base) == 41, f"Mezcla mal: {len(base)}"
    return base


TABLERO = _build_tablero()

# ----------------------------------------------------------------------------
# Parametros del minijuego (modelo: recoger monedas entre MIN y MAX).
# Se usa un promedio mu en la simulacion, y rango real en el juego.
# ----------------------------------------------------------------------------
META = 1500
TIROS = 3

MINIJUEGO_MIN = 5
MINIJUEGO_MAX = 20
MINIJUEGO_MULT = 20   # puntos por moneda en el minijuego


def minijuego_puntos_positivo(rng=None):
    rng = rng or random
    coins = rng.randint(MINIJUEGO_MIN, MINIJUEGO_MAX)
    return coins * MINIJUEGO_MULT


def minijuego_puntos_negativo(rng=None):
    rng = rng or random
    coins = rng.randint(MINIJUEGO_MIN, MINIJUEGO_MAX)
    return -(coins * MINIJUEGO_MULT)


def girar(rng=None, minijuego_fn_pos=None, minijuego_fn_neg=None):
    """
    Devuelve (casilla, es_combo).
    casilla es una tupla (tipo, valor, combo) ya con el valor del minijuego
    resuelto en caso de aplicar.
    """
    rng = rng or random
    minijuego_fn_pos = minijuego_fn_pos or minijuego_puntos_positivo
    minijuego_fn_neg = minijuego_fn_neg or minijuego_puntos_negativo
    idx = rng.randrange(len(TABLERO))
    tipo, valor, combo = TABLERO[idx]
    if tipo == 'minijuego':
        if valor == 1:  # casilla resta
            valor = minijuego_fn_neg(rng)
        else:           # casilla suma
            valor = minijuego_fn_pos(rng)
    return (tipo, valor, combo)


def jugar_partida(rng=None, minijuego_fn_pos=None, minijuego_fn_neg=None):
    """
    Juega una partida completa. Devuelve un dict con el resultado:
      - total:       puntos acumulados
      - gano:        bool, True si total >= META
      - perdio:      bool, True si cayo en 'Perdio'
      - tiros_usados: int (0..3)
      - tiros_combo:  int (combos encadenados)
      - historial:   lista de eventos jugables {'valor','combo','tipo'}
    """
    total = 0
    tiros_usados = 0
    tiros_combo = 0
    historial = []
    perdio = False
    gano = False

    while tiros_usados < TIROS and not perdio and total < META:
        tipo, valor, combo = girar(rng, minijuego_fn_pos, minijuego_fn_neg)
        historial.append({'tipo': tipo, 'valor': valor, 'combo': combo})

        if tipo == 'perdio':
            perdio = True
            total = 0
            break

        total += valor

        if combo:
            tiros_combo += 1
            # no gasta tiro, sigue girando en el mismo turno
        else:
            tiros_usados += 1

    gano = (not perdio) and total >= META
    return {
        'total': total,
        'gano': gano,
        'perdio': perdio,
        'tiros_usados': tiros_usados,
        'tiros_combo': tiros_combo,
        'historial': historial,
    }
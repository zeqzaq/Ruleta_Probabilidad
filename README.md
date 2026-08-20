# Ruleta - Juego de Azar

Proyecto de la materia **Probabilidad, Estadística y Métodos Numéricos**.
Juego de ruleta con puntos, tiros, combos, un minijuego de monedas y una
simulación Monte Carlo para estimar las probabilidades de ganar y perder.

## Instalación

```bash
pip install pygame matplotlib numpy
```

## Ejecutar

Todo se accede desde el menú:

```bash
python menu.py
```

O directamente cada módulo:

- **Jugar la ruleta** → `python ruleta.py`
- **Simulación + gráficos** → `python simulacion.py 200000` (200 000 partidas)
- **Solo minijuego** → `python minijuego.py`

## Reglas del juego

- Tablero de **41 casillas**.
- El jugador tiene **3 tiros**; cada tiro suma o resta puntos al total.
- Casillas con **`^`** (combo): aplican su valor **sin gastar tiro**
  (pueden encadenarse y siguen sumando al mismo turno).
- **`PERDIO`**: la partida termina inmediatamente con **0 puntos**.
- **`MINI+` / `MINI-`**: lanzan un minijuego donde el personaje corre y
  recoge monedas; las monedas se convierten en puntos (sumar o restar).
- **Se gana al alcanzar `>= 1500` puntos** al final de los tiros.

### Tablero (41 casillas)

| Casilla          | Cantidad |
|------------------|----------|
| +1000 / −1000    | 1 / 1    |
| +500  / −500     | 3 / 3    |
| +500^ / −500^    | 1 / 1    |
| +300  / −300     | 4 / 4    |
| +300^ / −300^    | 1 / 1    |
| +100  / −100     | 5 / 5    |
| +100^ / −100^    | 1 / 1    |
| +50              | 6        |
| PERDIO           | 1        |
| MINI+            | 1        |
| MINI-            | 1        |

## Resultados de la simulación (N = 100 000)

> Valores orientativos; ejecuta `simulacion.py` para reproducirlos.

- **P(GANAR) ≈ 2.0%**
- **P(derrota) ≈ 98.0%** (incluye la casilla PERDIO)
- **P(caer en PERDIO) ≈ 8.4%**
- **Puntos promedio ≈ +23** (desviación ≈ 644)

## Parámetros editables

En `ruleta_core.py`:

- `META` = 1500 → meta para ganar
- `TIROS` = 3 → cantidad de tiros
- `MINIJUEGO_MIN/MAX` y `MINIJUEGO_MULT` → puntos del minijuego

## Estructura

```
ruleta_core.py   -> reglas + tablero (fuente de verdad)
simulacion.py    -> Monte Carlo + histograma
ruleta.py        -> juego pygame
minijuego.py     -> minijuego recolector de monedas
menu.py          -> menu inicial
```
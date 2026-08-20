"""
simulacion.py
Simulacion Monte Carlo de la ruleta y graficos estadisticos.

Metodos numericos: estimacion de probabilidades por Monte Carlo (regla de
Laplace / frecuencia relativa). Estadistica: histograma de puntajes, media,
desviacion estandar e intervalos de confianza.

Uso:
    python simulacion.py
    python simulacion.py 500000     # numero custom de partidas
    python simulacion.py 200000 50  # N y cantidad de bins del histograma
"""

import sys
import math
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import numpy as np

import ruleta_core as core

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(x, **k):
        return x


def simular(N):
    """Corre N partidas y devuelve la lista de (total, perdio, gano)."""
    resultados = []
    for _ in tqdm(range(N), desc="Simulando"):
        r = core.jugar_partida()
        resultados.append((r['total'], r['perdio'], r['gano']))
    return resultados


def main():
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 200000
    bins = int(sys.argv[2]) if len(sys.argv) > 2 else 60

    resultados = simular(N)

    totales = np.array([r[0] for r in resultados])
    perdio = np.array([r[1] for r in resultados])
    gano = np.array([r[2] for r in resultados])

    p_ganar = gano.mean()
    p_perdio = perdio.mean()
    p_perder = 1.0 - p_ganar

    media = totales.mean()
    sd = totales.std(ddof=1)

    # intervalo de confianza 95% (aprox normal) para p_ganar
    z = 1.96
    margen = z * math.sqrt(p_ganar * (1 - p_ganar) / N)

    print("=" * 60)
    print(" SIMULACION MONTE CARLO -> RULETA")
    print(f" Partidas simuladas   : {N:,}")
    print(f" Meta para ganar      : {core.META} pts")
    print("=" * 60)
    print(f" P(GANAR)             : {p_ganar:.4%}   [{p_ganar-margen:.4%}, {p_ganar+margen:.4%}]")
    print(f" P(derrota)           : {p_perder:.4%}   (incluye Perdio)")
    print(f"  - P(caer en Perdio) : {p_perdio:.4%}")
    print("-" * 60)
    print(f" Puntos promedio      : {media:+.1f}")
    print(f" Desviacion estandar  : {sd:.1f}")
    print(f" Puntaje minimo       : {totales.min()}")
    print(f" Puntaje maximo       : {totales.max()}")
    print("=" * 60)

    # ----- grafico 1: histograma de puntajes finales -----
    fig, ax = plt.subplots(figsize=(10, 5.5))
    counts, edges, patches = ax.hist(
        totales, bins=bins, color="#4f8bc9", edgecolor="white", alpha=0.9,
        label="Puntajes finales",
    )
    ax.axvline(core.META, color="#d33", lw=2, ls="--",
               label=f"Meta = {core.META}")
    ax.axvline(media, color="#28a745", lw=2,
               label=f"Media = {media:.0f}")
    # resaltar la region de victoria
    ax.fill_betweenx([0, ax.get_ylim()[1]], core.META, totales.max(),
                     color="#f3c94f", alpha=0.25, label="Zona de victoria")
    ax.set_xlabel("Puntos acumulados")
    ax.set_ylabel("Frecuencia")
    ax.set_title(f"Distribucion de puntajes finales (N={N:,})")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig("histograma_puntajes.png", dpi=150)
    print(" Grafico guardado: histograma_puntajes.png")

    # ----- grafico 2: probabilidad de ganar vs cantidad de partidas (convergencia) -----
    acum = np.cumsum(gano)
    cum_est = np.arange(1, N + 1)
    fig2, ax2 = plt.subplots(figsize=(8, 4.5))
    ax2.plot(cum_est, acum / cum_est, color="#7b2cbf", lw=1.5)
    ax2.axhline(p_ganar, color="#d33", ls="--", label=f"valor final = {p_ganar:.4%}")
    ax2.set_xlabel("Partidas simuladas")
    ax2.set_ylabel("P(GANAR) estimada")
    ax2.set_title("Convergencia de la estimacion Monte Carlo")
    ax2.legend()
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig("convergencia.png", dpi=150)
    print(" Grafico guardado: convergencia.png")

    plt.show()


if __name__ == "__main__":
    main()
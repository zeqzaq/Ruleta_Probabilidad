"""
menu.py
Menu inicial del proyecto de la ruleta.

Opciones:
    1  -> Jugar la ruleta (pygame)
    2  -> Simulacion Monte Carlo + graficos
    q  -> Salir

    Mientras se juega: ESPACIO gira, R reinicia, ESC cerrar ventana.
"""

import sys


def main():
    print("=" * 60)
    print("          RULETA - Probabilidad, Estadistica y Metodos Numericos")
    print("=" * 60)
    print("  Tablero: 41 casillas | 3 tiros | Meta para ganar: 1500 pts")
    print("  Las casillas con '^' son COMBO (no gastan tiro).")
    print("  'PERDIO' derrota total. Los MINI son un minijuego de monedas.")
    print("-" * 60)
    print("  [1] Jugar la ruleta (pygame)")
    print("  [2] Simulacion Monte Carlo y graficos")
    print("  [q] Salir")
    print("-" * 60)

    while True:
        op = input("  Elige una opcion: ").strip().lower()
        if op == "1":
            import ruleta
            ruleta.main()
            return
        elif op == "2":
            import simulacion
            simulacion.main()
            return
        elif op == "q":
            print("  ¡Hasta luego!")
            sys.exit(0)
        else:
            print("  Opcion invalida. Usa 1, 2 o q.")


if __name__ == "__main__":
    main()
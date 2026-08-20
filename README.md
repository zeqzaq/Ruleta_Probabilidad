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

---

# Flujo de trabajo con Git y GitHub

Hoja de referencia para trabajar en equipo con este repositorio.

## 1. Copiar el proyecto en tu máquina (clonar)

Clona una sola vez desde GitHub a tu equipo:

```bash
git clone https://github.com/zeqzaq/Ruleta_Probabilidad.git
cd Ruleta_Probabilidad
```

Con esto ya tienes el proyecto, incluida la historia de `main` y todas las ramas.

## 2. Trabajar en tu propia rama (una por persona)

Las ramas ya creadas del equipo son: `Cristian`, `Pao`, `Felipe`, `Fer`.
Cada quien sube su trabajo a **su** rama, nunca directamente a `main`.

| Rama | Miembro |
|-------|---------|
| `main` | versión final del proyecto |
| `Cristian` | Cristian |
| `Pao` | Pao |
| `Felipe` | Felipe |
| `Fer` | Fer |

### Crear tu rama (la primera vez)

```bash
git checkout -b TuRama        # crea la rama TuRama y se posiciona en ella
git push -u origin TuRama     # la sube a GitHub por primera vez
```

Entre `-u` la primera vez para dejar configurada la relación "upstream";
después solo harás `git push`.

### Volver a tu rama ya existente

```bash
git checkout TuRama
git pull origin TuRama        # trae los últimos cambios de tu rama
```

## 3. Hacer un commit (guardar un cambio)

Ciclo típico mientras trabajas:

```bash
git add .                     # añade todos los cambios al "área de staging"
git status                    # revisa qué se va a subir
git commit -m "Describe brevemente el cambio"
git push                      # lo sube a tu rama en GitHub
```

Consejos:

- `git status` siempre muestra qué archivos están modificados antes de subir.
- El mensaje del `git commit -m` debe explicar **qué** cambiaste (ej.
  `"Ajusta puntos de la casilla MINI-"`).

## 4. Subir tu rama a `main` (merge)

Cuando tu trabajo esté terminado, se integra a `main`. El flujo recomendado es
unir `main` a tu rama primero para evitar conflictos, y luego tu rama a `main`:

```bash
git checkout main             # ve a la rama principal
git pull origin main          # asegúrate de tenerla al día
git merge TuRama              # integra los cambios de tu rama en main
git push                      # publica main actualizado en GitHub
```

Alternativa moderna (recomendada por GitHub): abrir un **Pull Request** en
`https://github.com/zeqzaq/Ruleta_Probabilidad/pull/new/TuRama` y hacer el merge
desde la interfaz web, donde además puedes revisar los cambios y cerrar
conflictos con más control.

## 5. Flujo de maestría (cómo mantener todo bajo control)

```bash
git branch                # lista las ramas y muestra en cuál estás
git status                # estado de tu copia de trabajo
git log --oneline         # historial de commits
git pull origin main      # actualiza tu rama con lo más nuevo de main
git push origin TuRama    # sube commits locales a tu rama en GitHub
```

## Ejemplo práctico de un ciclo completo

```bash
# 1) te pones en tu rama
git checkout Cristian
git pull origin Cristian

# 2) editas el código...

# 3) guardas
git add .
git commit -m "Agrega efecto de sonido a la ruleta"

# 4) subes tu rama
git push

# 5) integras a main
git checkout main
git pull origin main
git merge Cristian
git push
```

> **Regla de oro del equipo:** sube los cambios a tu propia rama y usa Pull
> Request (o el merge manual solo si dominas Git) para pasar a `main`. Así no se
> pisan los trabajos entre compañeros.
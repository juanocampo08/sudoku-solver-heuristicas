"""
Genera nuevos casos de prueba en datos/ en cada ejecución.

  - caso_pequeno : 5 celdas vacías
  - caso_mediano : 40 celdas vacías, solución única.
  - caso_grande  : 55 celdas vacías, solución única (26 pistas).
  - caso_extremo : transformación aleatoria del tablero clásico de 17 pistas,
    manteniendo 64 celdas vacías y solución única.

Los tableros pequeño, mediano y grande parten de un Sudoku resuelto, que se transforma
(permutación de dígitos, filas dentro de bandas, columnas dentro de pilas, bandas y pilas),
y luego se quitan celdas al azar manteniendo una solución única. El caso extremo se obtiene
transformando un tablero clásico de 17 pistas. La semilla aleatoria se guarda en los
comentarios de los archivos generados para identificar cada conjunto.

Uso:  python src/generar_datos.py
"""
import copy
import random

from utils import CARPETA_DATOS, contar_vacias, guardar_tablero, validar_tablero

TABLERO_BASE = [
    [5, 3, 4, 6, 7, 8, 9, 1, 2],
    [6, 7, 2, 1, 9, 5, 3, 4, 8],
    [1, 9, 8, 3, 4, 2, 5, 6, 7],
    [8, 5, 9, 7, 6, 1, 4, 2, 3],
    [4, 2, 6, 8, 5, 3, 7, 9, 1],
    [7, 1, 3, 9, 2, 4, 8, 5, 6],
    [9, 6, 1, 5, 3, 7, 2, 8, 4],
    [2, 8, 7, 4, 1, 9, 6, 3, 5],
    [3, 4, 5, 2, 8, 6, 1, 7, 9],
]

TABLERO_EXTREMO = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 3, 0, 8, 5],
    [0, 0, 1, 0, 2, 0, 0, 0, 0],
    [0, 0, 0, 5, 0, 7, 0, 0, 0],
    [0, 0, 4, 0, 0, 0, 1, 0, 0],
    [0, 9, 0, 0, 0, 0, 0, 0, 0],
    [5, 0, 0, 0, 0, 0, 0, 7, 3],
    [0, 0, 2, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 4, 0, 0, 0, 9],
]

def transformar(tablero, rnd):
    """Aplica transformaciones que preservan las reglas y las celdas vacías."""
    perm = list(range(1, 10))
    rnd.shuffle(perm)
    g = [[perm[v - 1] if v else 0 for v in fila] for fila in tablero]

    bandas = [0, 1, 2]
    rnd.shuffle(bandas)
    filas = []
    for b in bandas:
        interno = [b * 3 + i for i in range(3)]
        rnd.shuffle(interno)
        filas += interno
    g = [g[i] for i in filas]

    pilas = [0, 1, 2]
    rnd.shuffle(pilas)
    columnas = []
    for s in pilas:
        interno = [s * 3 + i for i in range(3)]
        rnd.shuffle(interno)
        columnas += interno
    return [[fila[j] for j in columnas] for fila in g]


def contar_soluciones(tablero, limite=2):
    """Cuenta soluciones (se detiene en `limite`). Backtracking con MRV sobre máscaras de bits."""
    validar_tablero(tablero)
    if type(limite) is not int or limite < 1:
        raise ValueError("el límite de soluciones debe ser un entero positivo")
    t = copy.deepcopy(tablero)
    filas, cols, cajas = [0] * 9, [0] * 9, [0] * 9
    vacias = []
    for f in range(9):
        for c in range(9):
            if t[f][c]:
                bit = 1 << t[f][c]
                filas[f] |= bit
                cols[c] |= bit
                cajas[f // 3 * 3 + c // 3] |= bit
            else:
                vacias.append((f, c))
    cuenta = 0

    def rec():
        nonlocal cuenta
        mejor, disp_mejor, n_mejor = None, 0, 10
        for (f, c) in vacias:
            if t[f][c]:
                continue
            disp = ~(filas[f] | cols[c] | cajas[f // 3 * 3 + c // 3]) & 0x3FE
            n = bin(disp).count("1")
            if n < n_mejor:
                mejor, disp_mejor, n_mejor = (f, c), disp, n
                if n == 0:
                    return
        if mejor is None:
            cuenta += 1
            return
        f, c = mejor
        while disp_mejor and cuenta < limite:
            bit = disp_mejor & -disp_mejor
            disp_mejor ^= bit
            t[f][c] = bit.bit_length() - 1
            filas[f] |= bit
            cols[c] |= bit
            cajas[f // 3 * 3 + c // 3] |= bit
            rec()
            t[f][c] = 0
            filas[f] ^= bit
            cols[c] ^= bit
            cajas[f // 3 * 3 + c // 3] ^= bit

    rec()
    return cuenta


def hacer_puzzle(solucion, n_vacias, rnd):
    """Quita hasta n_vacias celdas al azar manteniendo la solución única."""
    t = copy.deepcopy(solucion)
    celdas = [(f, c) for f in range(9) for c in range(9)]
    rnd.shuffle(celdas)
    quitadas = 0
    for (f, c) in celdas:
        if quitadas >= n_vacias:
            break
        valor = t[f][c]
        t[f][c] = 0
        if contar_soluciones(t) == 1:
            quitadas += 1
        else:
            t[f][c] = valor
    return t


def generar_caso(rnd, n_vacias):
    """Genera un caso de tamaño exacto y solución única."""
    for _ in range(100):
        solucion = transformar(TABLERO_BASE, rnd)
        tablero = hacer_puzzle(solucion, n_vacias, rnd)
        if contar_vacias(tablero) == n_vacias:
            return tablero
    raise RuntimeError(
        f"No se pudo generar un caso único con exactamente {n_vacias} celdas vacías "
        "después de 100 intentos"
    )


def main():
    CARPETA_DATOS.mkdir(exist_ok=True)
    semilla = random.SystemRandom().getrandbits(64)
    rnd = random.Random(semilla)

    casos = {
        "pequeno": (
            generar_caso(rnd, 5),
            "Generado aleatoriamente; solución única",
        ),
        "mediano": (
            generar_caso(rnd, 40),
            "Generado aleatoriamente; solución única",
        ),
        "grande": (
            generar_caso(rnd, 55),
            "Generado aleatoriamente; solución única",
        ),
        "extremo": (
            transformar(TABLERO_EXTREMO, rnd),
            "Transformación aleatoria de un tablero clásico de 17 pistas; solución única",
        ),
    }
    for nombre, (tablero, nota) in casos.items():
        ruta = CARPETA_DATOS / f"caso_{nombre}.txt"
        vacias = contar_vacias(tablero)
        guardar_tablero(tablero, ruta, [f"semilla del conjunto: {semilla}",
                                        f"caso_{nombre}: {vacias} celdas vacías ({81 - vacias} pistas)", nota,
                                        "Formato: 9 filas de 9 dígitos, 0 = celda vacía"])
        soluciones = contar_soluciones(tablero)
        if soluciones != 1:
            raise RuntimeError(
                f"{ruta.name}: se esperaba una solución única; se encontraron "
                f"{soluciones if soluciones else 'ninguna'}"
            )
        print(
            f"{ruta.name}: {vacias} vacías, soluciones={soluciones}, "
            f"semilla={semilla}"
        )


if __name__ == "__main__":
    main()
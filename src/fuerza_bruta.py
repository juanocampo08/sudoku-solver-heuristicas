import itertools
import time
import copy
import json

tablero_pequeno = [
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

def encontrar_celdas_vacias(tablero):
    """Devuelve la lista de posiciones (fila, columna) de todas las celdas vacías.""" 
    celdas_vacias = []
    for fila in range(9):
        for columna in range(9):
            if tablero[fila][columna] == 0:
                celdas_vacias.append((fila, columna))
    return celdas_vacias

def verificar_filas(tablero):
    for fila in range(9):
        valores = [v for v in tablero[fila] if v != 0]
        if len(valores) != len(set(valores)):
            return False
    return True


def verificar_columnas(tablero):
    for columna in range(9):
        valores = [tablero[fila][columna] for fila in range(9) if tablero[fila][columna] != 0]
        if len(valores) != len(set(valores)):
            return False
    return True

def verificar_caja(tablero, inicio_fila, inicio_columna):
    """Verifica que una caja 3x3 específica (dada por su esquina superior izquierda) no tenga números repetidos."""
    valores = []
    for f in range(inicio_fila, inicio_fila + 3):
        for c in range(inicio_columna, inicio_columna + 3):
            if tablero[f][c] != 0:
                valores.append(tablero[f][c])
    return len(valores) == len(set(valores))

def verificar_cajas(tablero):
    for inicio_fila in range(0, 9, 3):
        for inicio_columna in range(0, 9, 3):
            if not verificar_caja(tablero, inicio_fila, inicio_columna):
                return False
    return True

def verificar_tablero(tablero):
    return verificar_filas(tablero) and verificar_columnas(tablero) and verificar_cajas(tablero)

def fuerza_bruta_sudoku(tablero):
    """
    probando TODAS las combinaciones posibles para las
    celdas vacías y validando el tablero completo al final
    de cada combinación.
    """
    celdas_vacias = encontrar_celdas_vacias(tablero)
    n = len(celdas_vacias)

    for combinacion in itertools.product(range(1, 10), repeat=n):
        for (fila, columna), valor in zip(celdas_vacias, combinacion):
            tablero[fila][columna] = valor

        if verificar_tablero(tablero):
            return True

    return False


def imprimir_tablero(tablero):
    for fila in tablero:
        print(fila)

"""
print("Tablero original:")
imprimir_tablero(tablero_pequeno)

if fuerza_bruta_sudoku(tablero_pequeno):
    print("\nTablero resuelto (fuerza bruta):")
    imprimir_tablero(tablero_pequeno)
else:
    print("\nNo existe solución.")
"""


"""
Medicion empirica.
"""
def generar_tablero_prueba(n_vacias):
    """Toma el tablero base resuelto y vacía las últimas n_vacias celdas (en orden fila-major)."""
    tablero = copy.deepcopy(tablero_pequeno)
    posiciones = [(f, c) for f in range(9) for c in range(9)]
    for (f, c) in posiciones[-n_vacias:]:
        tablero[f][c] = 0
    return tablero

resultados = []
for n in [1, 2, 3, 4, 5, 6, 7]:
    tablero_prueba = generar_tablero_prueba(n)
    inicio = time.perf_counter()
    resuelto = fuerza_bruta_sudoku(tablero_prueba)
    fin = time.perf_counter()
    tiempo = fin - inicio
    combinaciones_teoricas = 9 ** n
    resultados.append({
        "n_celdas_vacias": n,
        "tiempo_segundos": tiempo,
        "combinaciones_teoricas": combinaciones_teoricas,
        "resuelto": resuelto
    })
    print(f"n={n} | tiempo={tiempo:.6f}s | 9^n={combinaciones_teoricas} | resuelto={resuelto}")

with open("resultados.json", "w") as f:
    json.dump(resultados, f, indent=2)
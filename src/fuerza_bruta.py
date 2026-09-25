import itertools

tablero_pequeno = [
    [5, 3, 4, 6, 0, 8, 9, 0, 2],
    [6, 7, 2, 1, 9, 5, 3, 4, 8],
    [1, 9, 8, 0, 4, 2, 0, 6, 7],
    [8, 5, 0, 7, 6, 1, 4, 0, 3],
    [4, 0, 6, 8, 0, 3, 0, 9, 1],
    [7, 1, 3, 9, 2, 0, 8, 5, 6],
    [9, 6, 1, 0, 3, 7, 2, 8, 4],
    [2, 0, 7, 4, 1, 9, 6, 3, 5],
    [3, 4, 5, 2, 8, 6, 1, 0, 0],
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
    return verificar_filas(tablero) and verificar_columnas(tablero)

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

print("Tablero original:")
imprimir_tablero(tablero_pequeno)

if fuerza_bruta_sudoku(tablero_pequeno):
    print("\nTablero resuelto (fuerza bruta):")
    imprimir_tablero(tablero_pequeno)
else:
    print("\nNo existe solución.")
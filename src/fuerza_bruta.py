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


def verificar_tablero(tablero):
    return verificar_filas(tablero) and verificar_columnas(tablero)


def imprimir_tablero(tablero):
    for fila in tablero:
        print(fila)




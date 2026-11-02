import copy
import time

from utils import cargar_tablero, es_solucion_valida, imprimir_tablero, listar_casos, validar_tablero


def es_valido(tablero, fila, columna, numero):
    """Revisa si el número se puede poner en esa celda sin repetirse."""
    for i in range(9):
        if tablero[fila][i] == numero or tablero[i][columna] == numero:
            return False

    inicio_fila = fila // 3 * 3
    inicio_columna = columna // 3 * 3
    for f in range(inicio_fila, inicio_fila + 3):
        for c in range(inicio_columna, inicio_columna + 3):
            if tablero[f][c] == numero:
                return False
    return True


def buscar_vacia(tablero):
    """Devuelve (fila, columna) de la primera celda vacía, o None si no hay."""
    for fila in range(9):
        for columna in range(9):
            if tablero[fila][columna] == 0:
                return fila, columna
    return None


def resolver(tablero):
    """Resuelve el sudoku sobre el mismo tablero. Devuelve True si encontró solución."""
    solucion, _ = resolver_backtracking(tablero, usar_mrv=False)
    if solucion is None:
        return False
    for fila in range(9):
        tablero[fila][:] = solucion[fila]
    return True


def resolver_backtracking(tablero, usar_mrv=True, max_nodos=None):
    """Devuelve (solución, estadísticas), o (None, estadísticas) si no se resuelve."""
    validar_tablero(tablero)
    original = copy.deepcopy(tablero)
    trabajo = copy.deepcopy(tablero)
    estadisticas = {"nodos": 0, "retrocesos": 0, "excedido": False}
    filas_usadas = [0] * 9
    columnas_usadas = [0] * 9
    cajas_usadas = [0] * 9
    for fila in range(9):
        for columna in range(9):
            numero = trabajo[fila][columna]
            if numero:
                bit = 1 << numero
                filas_usadas[fila] |= bit
                columnas_usadas[columna] |= bit
                cajas_usadas[fila // 3 * 3 + columna // 3] |= bit

    def disponibles(fila, columna):
        caja = fila // 3 * 3 + columna // 3
        return 0x3FE & ~(filas_usadas[fila] | columnas_usadas[columna] | cajas_usadas[caja])

    def buscar():
        if max_nodos is not None and estadisticas["nodos"] >= max_nodos:
            estadisticas["excedido"] = True
            return False
        estadisticas["nodos"] += 1

        if usar_mrv:
            mejor = None
            mejores_candidatos = None
            for fila in range(9):
                for columna in range(9):
                    if trabajo[fila][columna] != 0:
                        continue
                    mascara = disponibles(fila, columna)
                    if not mascara:
                        return False
                    if mejores_candidatos is None or mascara.bit_count() < len(mejores_candidatos):
                        mejor = (fila, columna)
                        mejores_candidatos = []
                        while mascara:
                            bit = mascara & -mascara
                            mejores_candidatos.append(bit.bit_length() - 1)
                            mascara ^= bit
            if mejor is None:
                return es_solucion_valida(trabajo, original)
            fila, columna = mejor
            candidatos = mejores_candidatos
        else:
            vacia = buscar_vacia(trabajo)
            if vacia is None:
                return es_solucion_valida(trabajo, original)
            fila, columna = vacia
            mascara = disponibles(fila, columna)
            candidatos = []
            while mascara:
                bit = mascara & -mascara
                candidatos.append(bit.bit_length() - 1)
                mascara ^= bit

        for numero in candidatos:
            bit = 1 << numero
            caja = fila // 3 * 3 + columna // 3
            trabajo[fila][columna] = numero
            filas_usadas[fila] |= bit
            columnas_usadas[columna] |= bit
            cajas_usadas[caja] |= bit
            if buscar():
                return True
            trabajo[fila][columna] = 0
            filas_usadas[fila] ^= bit
            columnas_usadas[columna] ^= bit
            cajas_usadas[caja] ^= bit
            if estadisticas["excedido"]:
                return False
            estadisticas["retrocesos"] += 1
        return False

    if buscar():
        return trabajo, estadisticas
    return None, estadisticas
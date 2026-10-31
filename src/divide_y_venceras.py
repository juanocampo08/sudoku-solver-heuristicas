import itertools
import time

from backtracking import es_valido
from utils import (
    cargar_tablero,
    es_solucion_valida,
    imprimir_tablero,
    listar_casos,
    validar_tablero,
)


def completar_fila(tablero, fila):
    """CASO BASE: devuelve todas las formas de llenar una fila sin chocar con las pistas."""
    vacias = [c for c in range(9) if tablero[fila][c] == 0]
    faltantes = [n for n in range(1, 10) if n not in tablero[fila]]

    opciones = []
    for orden in itertools.permutations(faltantes):
        if all(es_valido(tablero, fila, c, n) for c, n in zip(vacias, orden)):
            nueva = tablero[fila][:]
            for c, n in zip(vacias, orden):
                nueva[c] = n
            opciones.append([nueva])
    return opciones


def hay_repetidos(filas, fila_inicial):
    """Revisa si las filas dadas repiten algún número en una columna o en una caja."""
    for c in range(9):
        columna = [fila[c] for fila in filas]
        if len(set(columna)) < len(columna):
            return True

    for banda in range(3):
        for col_inicial in range(0, 9, 3):
            valores = []
            for i, fila in enumerate(filas):
                if (fila_inicial + i) // 3 == banda:
                    valores += fila[col_inicial:col_inicial + 3]
            if len(set(valores)) < len(valores):
                return True
    return False


def resolver_filas(tablero, inicio, fin, estadisticas=None, max_combinaciones=None):
    """Devuelve todas las soluciones posibles para las filas desde inicio hasta fin (sin incluir fin)."""
    if estadisticas is not None and estadisticas["excedido"]:
        return []
    if fin - inicio == 1:
        opciones = completar_fila(tablero, inicio)
        if estadisticas is not None and inicio % 3 == 0:
            estadisticas["parciales_por_banda"][inicio // 3] = len(opciones)
        return opciones

    # DIVIDIR: si hay más de una banda se corta en el límite de una banda; si no, una fila y el resto
    medio = inicio + 3 if fin - inicio > 3 else inicio + 1

    # VENCER: cada mitad se resuelve por separado
    izquierda = resolver_filas(tablero, inicio, medio, estadisticas, max_combinaciones)
    if not izquierda:
        return []
    derecha = resolver_filas(tablero, medio, fin, estadisticas, max_combinaciones)

    # COMBINAR: solo se unen las mitades que no repiten números en columnas ni cajas
    combinadas = []
    for filas_izq in izquierda:
        for filas_der in derecha:
            if estadisticas is not None:
                if max_combinaciones is not None and estadisticas["combinaciones"] >= max_combinaciones:
                    estadisticas["excedido"] = True
                    return combinadas
                estadisticas["combinaciones"] += 1
            filas = filas_izq + filas_der
            if not hay_repetidos(filas, inicio):
                combinadas.append(filas)
            if estadisticas is not None and estadisticas["excedido"]:
                return combinadas
    if estadisticas is not None and fin - inicio == 3 and inicio % 3 == 0:
        estadisticas["parciales_por_banda"][inicio // 3] = len(combinadas)
    return combinadas


def resolver_dyv(tablero, max_combinaciones=None):
    """Devuelve (solución, estadísticas) sin modificar el tablero recibido."""
    validar_tablero(tablero)
    estadisticas = {
        "parciales_por_banda": [0, 0, 0],
        "combinaciones": 0,
        "soluciones": 0,
        "excedido": False,
    }
    soluciones = resolver_filas(tablero, 0, 9, estadisticas, max_combinaciones)
    estadisticas["soluciones"] = len(soluciones)
    solucion = soluciones[0] if soluciones else None
    if solucion is not None and not es_solucion_valida(solucion, tablero):
        raise RuntimeError("divide y vencerás produjo una solución inválida")
    return solucion, estadisticas


def resolver(tablero):
    """Devuelve el tablero resuelto, o None si no hay solución. No modifica el original."""
    solucion, _ = resolver_dyv(tablero)
    return solucion
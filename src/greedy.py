import copy
import time

from backtracking import es_valido
from utils import cargar_tablero, contar_vacias, es_solucion_valida, listar_casos, validar_tablero


def candidatos(tablero, fila, columna):
    """Números que se pueden poner en una celda sin chocar con fila, columna o caja."""
    return [n for n in range(1, 10) if es_valido(tablero, fila, columna, n)]


def resolver_greedy(tablero):
    """
    Decisión local: llenar la celda con MENOS candidatos, con su primer candidato.
    Nunca se deshace una decisión. Devuelve (tablero, resuelto).
    Si se atasca, el tablero queda como estaba en ese momento.
    """
    validar_tablero(tablero)
    original = copy.deepcopy(tablero)
    tablero = copy.deepcopy(tablero)

    while True:
        mejor_celda = None
        mejores_candidatos = None

        for fila in range(9):
            for columna in range(9):
                if tablero[fila][columna] != 0:
                    continue
                lista = candidatos(tablero, fila, columna)
                if not lista:
                    return tablero, False  # celda sin opciones: el greedy se atascó
                if mejores_candidatos is None or len(lista) < len(mejores_candidatos):
                    mejor_celda = (fila, columna)
                    mejores_candidatos = lista

        if mejor_celda is None:
            return tablero, es_solucion_valida(tablero, original)

        fila, columna = mejor_celda
        tablero[fila][columna] = mejores_candidatos[0]
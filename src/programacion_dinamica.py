import time

from divide_y_venceras import completar_fila
from utils import cargar_tablero, es_solucion_valida, listar_casos, validar_tablero


def cabe(opcion, columnas, cajas):
    """True si la fila no repite números con lo ya usado en columnas y cajas."""
    for c in range(9):
        if opcion[c] in columnas[c]:
            return False
    for k in range(3):
        if cajas[k] & set(opcion[3 * k:3 * k + 3]):
            return False
    return True


def resolver(tablero, max_estados=None):
    """
    Programación dinámica con memoización, fila por fila.

    Estado: (fila, números usados en cada columna, números usados en cada caja de la banda).
    Lo que ya se puso en las filas anteriores solo importa a través de ese estado, así que
    muchos caminos distintos llegan al mismo estado y se resuelve una sola vez.
    """
    validar_tablero(tablero)
    opciones = [[o[0] for o in completar_fila(tablero, f)] for f in range(9)]
    memoria = {}
    visitas = {"estados": 0, "reutilizados": 0}

    def resolver_desde(fila, columnas, cajas):
        """Devuelve las filas que faltan desde 'fila' (lista de filas), o None si no se puede."""
        if fila == 9:
            return []
        if fila % 3 == 0:
            cajas = (frozenset(), frozenset(), frozenset())  # empieza una banda nueva

        estado = (fila, columnas, cajas)
        if estado in memoria:
            visitas["reutilizados"] += 1
            return memoria[estado]
        if max_estados is not None and visitas["estados"] >= max_estados:
            visitas["excedido"] = True
            return None
        visitas["estados"] += 1

        resultado = None
        for opcion in opciones[fila]:
            if cabe(opcion, columnas, cajas):
                nuevas_columnas = tuple(columnas[c] | {opcion[c]} for c in range(9))
                nuevas_cajas = tuple(cajas[k] | set(opcion[3 * k:3 * k + 3]) for k in range(3))
                resto = resolver_desde(fila + 1, nuevas_columnas, nuevas_cajas)
                if resto is not None:
                    resultado = [opcion] + resto
                    break
                if visitas.get("excedido"):
                    break

        memoria[estado] = resultado
        return resultado

    sin_usar = tuple(frozenset() for _ in range(9))
    solucion = resolver_desde(0, sin_usar, (frozenset(),) * 3)
    if solucion is not None and not es_solucion_valida(solucion, tablero):
        raise RuntimeError("programación dinámica produjo una solución inválida")
    return solucion, visitas
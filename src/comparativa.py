"""
Ejecuta las soluciones sobre todos los casos de datos/ y compara tiempos.

Uso:
  python src/comparativa.py

Salida: tabla en consola, docs/resultados.json y (si hay matplotlib) docs/comparativa.png.

Este módulo también lo usa la interfaz gráfica (src/main.py): `comparar` y `ejecutar_tecnica`
contienen la lógica de medición y los límites, para que consola e interfaz no la dupliquen.
"""
import copy
import json
import logging
import time

from backtracking import resolver_backtracking
from divide_y_venceras import resolver_dyv
from greedy import resolver_greedy
from programacion_dinamica import resolver as resolver_programacion_dinamica
from fuerza_bruta import resolver_fuerza_bruta
from utils import (
    RAIZ,
    cargar_tablero,
    contar_vacias,
    es_solucion_valida,
    imprimir_tablero,
    listar_casos,
)

logger = logging.getLogger(__name__)

MAX_COMBINACIONES_FB = 100_000
MAX_NODOS_BT = 100_000
MAX_COMBINACIONES_DYV = 100_000
MAX_ESTADOS_DP = 10_000
REPETICIONES = 3           # se reporta el mejor tiempo de N ejecuciones
MAX_VACIAS_DYV_DP = 55     # por encima, la generación de permutaciones puede crecer mucho
MAX_VACIAS_REPETIR = 40    # por encima de esto cada método se ejecuta una sola vez

TECNICAS_LIMITADAS = ("Divide y vencerás (bandas)", "Programación dinámica")


def medir(funcion, repeticiones=REPETICIONES):
    """Ejecuta `funcion` varias veces y devuelve (mejor_tiempo, solucion, stats)."""
    mejor, solucion, stats = None, None, None
    for _ in range(repeticiones):
        inicio = time.perf_counter()
        solucion, stats = funcion()
        seg = time.perf_counter() - inicio
        mejor = seg if mejor is None else min(mejor, seg)
        if stats.get("excedido"):
            break  # no tiene sentido repetir una ejecución que ya superó el límite
    return mejor, solucion, stats


def estado(solucion, stats, original):
    if stats.get("excedido"):
        return "excedió límite"
    if solucion is None:
        return "sin solución"
    return "OK" if es_solucion_valida(solucion, original) else "SOLUCIÓN INVÁLIDA"


def describir_estadisticas(stats):
    """Resume en una línea las estadísticas que devuelve cada método."""

    if "nodos" in stats:
        return f"nodos={stats['nodos']}, retrocesos={stats['retrocesos']}"
    if "parciales_por_banda" in stats:
        return f"parciales/banda={stats['parciales_por_banda']}"
    if "estados" in stats:
        return f"estados={stats['estados']}, reutilizados={stats['reutilizados']}"
    if "combinaciones" in stats:
        return f"combinaciones={stats['combinaciones']}"
    if stats.get("excedido"):
        return "se alcanzó el límite de cálculo"
    return "sin estadísticas"


def resolver_greedy_comparable(original):
    solucion, resuelto = resolver_greedy(original)
    return (solucion if resuelto else None), {}


def resolver_dyv_comparable(original):
    return resolver_dyv(original, max_combinaciones=MAX_COMBINACIONES_DYV)


def resolver_dp_comparable(original):
    return resolver_programacion_dinamica(original, max_estados=MAX_ESTADOS_DP)


def obtener_tecnicas():
    """Devuelve los métodos de resolución y sus límites compartidos."""
    return [
        ("Fuerza Bruta", lambda o: resolver_fuerza_bruta(o, max_combinaciones=MAX_COMBINACIONES_FB)),
        ("Backtracking (orden fijo)", lambda o: resolver_backtracking(o, usar_mrv=False, max_nodos=MAX_NODOS_BT)),
        ("Backtracking + MRV", lambda o: resolver_backtracking(o, usar_mrv=True)),
        ("Divide y vencerás (bandas)", resolver_dyv_comparable),
        ("Programación dinámica", resolver_dp_comparable),
        ("Greedy", resolver_greedy_comparable),
    ]


def ejecutar_tecnica(nombre_caso, original, etiqueta, funcion):
    """
    Ejecuta un método sobre un caso y devuelve un diccionario con el resultado:
    caso, vacias, tecnica, tiempo_s, estado, detalle, solucion (o None) y stats.
    """
    vacias = contar_vacias(original)
    resultado = {
        "caso": nombre_caso,
        "vacias": vacias,
        "tecnica": etiqueta,
        "tiempo_s": None,
        "estado": "",
        "detalle": "",
        "solucion": None,
        "stats": {},
    }

    if vacias > MAX_VACIAS_DYV_DP and etiqueta in TECNICAS_LIMITADAS:
        resultado["estado"] = "no ejecutado"
        resultado["detalle"] = f"omitido: más de {MAX_VACIAS_DYV_DP} celdas vacías"
        return resultado

    repeticiones = REPETICIONES if vacias <= MAX_VACIAS_REPETIR else 1
    try:
        tiempo, solucion, stats = medir(lambda: funcion(copy.deepcopy(original)), repeticiones)
    except Exception as error:  # un método que falla no debe detener la comparación completa
        logger.exception("Falló %s en el caso %s", etiqueta, nombre_caso)
        resultado["estado"] = "ERROR"
        resultado["detalle"] = f"{type(error).__name__}: {error}"
        return resultado

    resultado["tiempo_s"] = tiempo
    resultado["estado"] = estado(solucion, stats, original)
    resultado["detalle"] = describir_estadisticas(stats)
    resultado["stats"] = stats
    if resultado["estado"] == "OK":
        resultado["solucion"] = solucion
    return resultado


def comparar(casos, tecnicas, al_avanzar=None):
    """
    Ejecuta cada método en cada caso (agrupado por caso) y devuelve la lista de resultados.

    casos: dict {nombre: tablero}.  tecnicas: lista de (etiqueta, funcion).
    al_avanzar(hechas, total, caso, etiqueta): se llama antes de cada ejecución (opcional).
    """
    total = len(casos) * len(tecnicas)
    resultados = []
    for nombre, original in casos.items():
        for etiqueta, funcion in tecnicas:
            if al_avanzar:
                al_avanzar(len(resultados), total, nombre, etiqueta)
            resultados.append(ejecutar_tecnica(nombre, original, etiqueta, funcion))
    return resultados


def imprimir_resultados(casos, tecnicas, resultados):
    print("SUDOKUS ORIGINALES")
    for nombre, original in casos.items():
        print(f"\nCaso {nombre}:")
        imprimir_tablero(original)

    for etiqueta, _ in tecnicas:
        print(f"\nSOLUCIONES CON {etiqueta.upper()}")
        for r in resultados:
            if r["tecnica"] != etiqueta:
                continue
            print(f"\nCaso {r['caso']}: {r['estado']} ({r['detalle']})")
            if r["solucion"] is not None:
                imprimir_tablero(r["solucion"])
            elif r["estado"] == "no ejecutado":
                print("No se ejecutó por el límite de celdas vacías.")
            else:
                print("El método no encontró una solución completa.")


def imprimir_tabla(resultados):
    print("\nCOMPARATIVA")
    print(f"{'caso':9s}{'vacías':>7s}  {'técnica':28s}{'tiempo (s)':>12s}  {'detalle':38s} estado")
    print("-" * 110)
    for r in resultados:
        tiempo = "—" if r["tiempo_s"] is None else f"{r['tiempo_s']:.5f}"
        print(f"{r['caso']:9s}{r['vacias']:>7d}  {r['tecnica']:28s}{tiempo:>12s}  {r['detalle']:38s} {r['estado']}")


def guardar_resultados(resultados, destino):
    registros = [{k: v for k, v in r.items() if k != "solucion"} for r in resultados]
    with open(destino, "w", encoding="utf-8") as archivo:
        json.dump(registros, archivo, indent=2, ensure_ascii=False)
    print(f"\nResultados guardados en {destino}")


def main(mostrar_tableros=False):
    casos = {nombre: cargar_tablero(ruta) for nombre, ruta in listar_casos()}
    if not casos:
        print("No hay casos en datos/. Ejecuta primero: python src/generar_datos.py")
        return
    tecnicas = obtener_tecnicas()
    resultados = comparar(casos, tecnicas)

    if mostrar_tableros:
        imprimir_resultados(casos, tecnicas, resultados)
    imprimir_tabla(resultados)

    destino = RAIZ / "docs"
    destino.mkdir(exist_ok=True)
    guardar_resultados(resultados, destino / "resultados.json")
    graficar(resultados, destino / "comparativa.png")


def graficar(resultados, ruta):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib no está instalado: se omite la gráfica (pip install matplotlib)")
        return
    tecnicas = sorted({r["tecnica"] for r in resultados})
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for tecnica in tecnicas:
        puntos = [(r["vacias"], r["tiempo_s"]) for r in resultados
                  if r["tecnica"] == tecnica and r["tiempo_s"] and r["estado"] == "OK"]
        if puntos:
            xs, ys = zip(*sorted(puntos))
            ax.plot(xs, ys, marker="o", label=tecnica)
    ax.set_yscale("log")
    ax.set_xlabel("Celdas vacías (n)")
    ax.set_ylabel("Tiempo (s, escala log)")
    ax.set_title("Sudoku: tiempo vs. celdas vacías (solo ejecuciones completadas)")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(ruta, dpi=150)
    print(f"Gráfica guardada en {ruta}")


if __name__ == "__main__":
    main()

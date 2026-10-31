"""
Utilidades compartidas: carga de casos de prueba, impresión y validación de tableros.

Formato de los archivos en datos/:
  - 9 líneas de 9 caracteres; '0' (o '.') representa una celda vacía.
  - Las líneas que empiezan con '#' son comentarios y se ignoran.
"""
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CARPETA_DATOS = RAIZ / "datos"


def cargar_tablero(ruta):
    """Lee un archivo de datos y devuelve el tablero como lista de 9 listas de 9 enteros."""
    tablero = []
    for linea in Path(ruta).read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#"):
            continue
        contenido = linea.replace(" ", "")
        if any(ch not in "0123456789." for ch in contenido):
            raise ValueError(f"{ruta}: se encontró un carácter inválido en el tablero")
        fila = [0 if ch == "." else int(ch) for ch in contenido]
        tablero.append(fila)
    validar_tablero(tablero)
    return tablero


def guardar_tablero(tablero, ruta, comentarios=()):
    """Guarda un tablero en el formato de datos/ (con comentarios opcionales)."""
    validar_tablero(tablero)
    lineas = [f"# {c}" for c in comentarios]
    lineas += ["".join(str(v) for v in fila) for fila in tablero]
    Path(ruta).write_text("\n".join(lineas) + "\n", encoding="utf-8")


def listar_casos():
    """Devuelve [(nombre, ruta)] de los casos en datos/, ordenados por tamaño de caso."""
    orden = ["pequeno", "mediano", "grande", "extremo"]
    archivos = {p.stem.replace("caso_", ""): p for p in CARPETA_DATOS.glob("caso_*.txt")}
    nombres = [n for n in orden if n in archivos] + sorted(n for n in archivos if n not in orden)
    return [(n, archivos[n]) for n in nombres]


def contar_vacias(tablero):
    return sum(1 for fila in tablero for v in fila if v == 0)


def validar_tablero(tablero):
    """Valida dimensiones, valores y consistencia; lanza ValueError si no es válido."""
    if len(tablero) != 9 or any(len(fila) != 9 for fila in tablero):
        raise ValueError("el tablero debe ser de 9x9")
    if any(type(valor) is not int or not 0 <= valor <= 9 for fila in tablero for valor in fila):
        raise ValueError("las celdas deben ser enteros entre 0 y 9")
    if not es_consistente(tablero):
        raise ValueError("el tablero contiene números repetidos en una fila, columna o caja")


def imprimir_tablero(tablero):
    for fila in tablero:
        print(fila)


def _sin_repetidos(valores):
    valores = [v for v in valores if v != 0]
    return len(valores) == len(set(valores))


def es_consistente(tablero):
    """True si ninguna fila, columna o caja tiene números repetidos (ignora ceros)."""
    for i in range(9):
        if not _sin_repetidos(tablero[i]):
            return False
        if not _sin_repetidos([tablero[f][i] for f in range(9)]):
            return False
    for f0 in range(0, 9, 3):
        for c0 in range(0, 9, 3):
            if not _sin_repetidos([tablero[f][c] for f in range(f0, f0 + 3) for c in range(c0, c0 + 3)]):
                return False
    return True


def es_solucion_valida(tablero, original=None):
    """True si el tablero está completo, es consistente y (si se da) respeta los datos del original."""
    try:
        validar_tablero(tablero)
        if original is not None:
            validar_tablero(original)
    except (TypeError, ValueError):
        return False
    if any(v == 0 for fila in tablero for v in fila) or not es_consistente(tablero):
        return False
    if original is not None:
        return all(original[f][c] in (0, tablero[f][c]) for f in range(9) for c in range(9))
    return True

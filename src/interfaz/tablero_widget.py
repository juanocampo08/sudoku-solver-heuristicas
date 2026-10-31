"""Widget que dibuja un tablero de Sudoku 9x9 y se adapta al tamaño disponible."""
import tkinter as tk

from interfaz.tema import COLORES

MARGEN = 6


class TableroCanvas(tk.Canvas):
    """
    Dibuja el tablero sobre un Canvas.

    - mostrar(tablero): todas las cifras se muestran como pistas.
    - mostrar(tablero, original): las cifras que no estaban en `original` se resaltan como
      resueltas por el método.
    - mostrar_mensaje(texto): tablero vacío con un aviso en el centro.
    """

    def __init__(self, padre, fuente_digito, fuente_mensaje, **opciones):
        super().__init__(padre, bg=COLORES["panel"], highlightthickness=0, **opciones)
        self.fuente_digito = fuente_digito
        self.fuente_mensaje = fuente_mensaje
        self.tablero = None
        self.original = None
        self.mensaje = None
        self.bind("<Configure>", lambda evento: self._dibujar())

    def mostrar(self, tablero, original=None):
        self.tablero, self.original, self.mensaje = tablero, original, None
        self._dibujar()

    def mostrar_mensaje(self, texto):
        self.tablero, self.original, self.mensaje = None, None, texto
        self._dibujar()

    def _dibujar(self):
        ancho, alto = self.winfo_width(), self.winfo_height()
        celda = (min(ancho, alto) - 2 * MARGEN) // 9
        if celda < 8:
            return
        lado = celda * 9
        x0, y0 = (ancho - lado) // 2, (alto - lado) // 2

        self.delete("all")
        self.fuente_digito.configure(size=-int(celda * 0.56))  # negativo = píxeles

        for fila in range(9):
            for columna in range(9):
                x, y = x0 + columna * celda, y0 + fila * celda
                valor = self.tablero[fila][columna] if self.tablero else 0
                es_resuelta = bool(
                    valor and self.original is not None and self.original[fila][columna] == 0
                )
                self.create_rectangle(
                    x, y, x + celda, y + celda, outline="",
                    fill=COLORES["celda_resuelta"] if es_resuelta else COLORES["celda"],
                )
                if valor:
                    self.create_text(
                        x + celda / 2, y + celda / 2, text=str(valor), font=self.fuente_digito,
                        fill=COLORES["resuelta"] if es_resuelta else COLORES["pista"],
                    )

        for i in range(10):
            gruesa = i % 3 == 0
            color = COLORES["linea_gruesa"] if gruesa else COLORES["linea_fina"]
            grosor = 2 if gruesa else 1
            self.create_line(x0, y0 + i * celda, x0 + lado, y0 + i * celda, fill=color, width=grosor)
            self.create_line(x0 + i * celda, y0, x0 + i * celda, y0 + lado, fill=color, width=grosor)

        if self.mensaje:
            self._dibujar_mensaje(ancho, alto, lado)

    def _dibujar_mensaje(self, ancho, alto, lado):
        texto = self.create_text(
            ancho / 2, alto / 2, text=self.mensaje, font=self.fuente_mensaje,
            fill=COLORES["texto"], width=int(lado * 0.74), justify="center",
        )
        x1, y1, x2, y2 = self.bbox(texto)
        fondo = self.create_rectangle(
            x1 - 18, y1 - 14, x2 + 18, y2 + 14,
            fill=COLORES["panel"], outline=COLORES["borde"], width=1,
        )
        self.tag_lower(fondo, texto)

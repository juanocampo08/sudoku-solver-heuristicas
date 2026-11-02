"""
Ventana principal: coloca los widgets y conecta la interfaz con la comparación.

Aquí no hay lógica de Sudoku ni colores: los algoritmos y la medición están en
comparativa.py, y el aspecto en tema.py y tablero_widget.py.
"""
import logging
import queue
import threading
import tkinter as tk
from tkinter import messagebox, ttk

from comparativa import comparar, obtener_tecnicas
from interfaz import tema
from interfaz.tablero_widget import TableroCanvas
from utils import contar_vacias

logger = logging.getLogger(__name__)

ETIQUETAS_ESTADO = {
    "OK": "Válida",
    "excedió límite": "Límite alcanzado",
    "no ejecutado": "Omitido",
    "sin solución": "Sin solución",
    "SOLUCIÓN INVÁLIDA": "Solución inválida",
    "ERROR": "Error",
}
COLOR_ESTADO = {"OK": "ok", "excedió límite": "aviso", "no ejecutado": "aviso"}


def formato_tiempo(segundos):
    if segundos is None:
        return "—"
    if segundos < 1:
        return f"{segundos * 1000:.2f} ms"
    return f"{segundos:.2f} s"


class SudokuApp:
    def __init__(self, root, casos):
        self.root = root
        self.casos = casos
        self.tecnicas = obtener_tecnicas()
        self.resultados = []
        self.cola = queue.Queue()

        self.fuentes = tema.crear_fuentes(root)
        tema.configurar_estilos(root, self.fuentes)

        self.caso_actual = tk.StringVar(value=next(iter(casos)))
        self.tecnica_actual = tk.StringVar(value=self.tecnicas[0][0])
        self.seleccion = {nombre: tk.BooleanVar(value=True) for nombre, _ in self.tecnicas}
        self.estado_texto = tk.StringVar(value="Elige los métodos y pulsa «Comparar métodos».")
        self.original_subtitulo = tk.StringVar()
        self.solucion_subtitulo = tk.StringVar()
        self.mas_rapido_valor = tk.StringVar()
        self.mas_rapido_detalle = tk.StringVar()
        self.cobertura_valor = tk.StringVar()
        self.cobertura_detalle = tk.StringVar()

        self._configurar_ventana()
        self._construir()
        self._mostrar_caso()

    # ---------- construcción de la ventana ----------

    def _configurar_ventana(self):
        pantalla_ancho = self.root.winfo_screenwidth()
        pantalla_alto = self.root.winfo_screenheight()
        ancho = min(1120, pantalla_ancho - 80)
        alto = min(720, pantalla_alto - 100)
        x = (pantalla_ancho - ancho) // 2
        y = max(0, (pantalla_alto - alto) // 3)
        self.root.title("Sudoku · Laboratorio de algoritmos")
        self.root.geometry(f"{ancho}x{alto}+{x}+{y}")
        self.root.minsize(min(980, ancho), min(600, alto))

    def _construir(self):
        contenedor = ttk.Frame(self.root, padding=(20, 16))
        contenedor.pack(fill="both", expand=True)
        contenedor.columnconfigure(1, weight=1)
        contenedor.rowconfigure(1, weight=1)

        cabecera = ttk.Frame(contenedor)
        cabecera.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 14))
        cabecera.columnconfigure(0, weight=1)
        titulos = ttk.Frame(cabecera)
        titulos.grid(row=0, column=0, sticky="w")
        ttk.Label(titulos, text="Laboratorio de Sudoku", style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(
            titulos, text="Compara técnicas sobre los mismos tableros.",
            style="Suave.TLabel",
        ).pack(anchor="w")
        self._bloque_resumen(
            cabecera, 1, "MÁS RÁPIDO EN ESTE CASO", self.mas_rapido_valor,
            self.mas_rapido_detalle, "Metrica.TLabel",
        )
        self._bloque_resumen(
            cabecera, 2, "MAYOR COBERTURA", self.cobertura_valor,
            self.cobertura_detalle, "MetricaAcento.TLabel",
        )

        self._construir_lateral(contenedor).grid(row=1, column=0, sticky="ns", padx=(0, 16))
        self._construir_principal(contenedor).grid(row=1, column=1, sticky="nsew")

    @staticmethod
    def _tarjeta(padre, padx=14, pady=12):
        return tk.Frame(
            padre, bg=tema.COLORES["panel"], padx=padx, pady=pady,
            highlightbackground=tema.COLORES["borde"], highlightthickness=1,
        )

    @staticmethod
    def _seccion(padre, texto, fila, arriba=0):
        ttk.Label(padre, text=texto, style="Seccion.TLabel").grid(
            row=fila, column=0, sticky="w", pady=(arriba, 3)
        )

    def _bloque_resumen(self, padre, columna, titulo, valor, detalle, estilo_valor):
        bloque = self._tarjeta(padre, padx=12, pady=6)
        bloque.grid(row=0, column=columna, sticky="ns", padx=(12, 0))
        self._seccion(bloque, titulo, 0)
        ttk.Label(bloque, textvariable=valor, style=estilo_valor, width=22).grid(row=1, column=0, sticky="w")
        ttk.Label(bloque, textvariable=detalle, style="TarjetaSuave.TLabel").grid(
            row=2, column=0, sticky="w"
        )

    def _construir_lateral(self, padre):
        tarjeta = self._tarjeta(padre)
        tarjeta.columnconfigure(0, weight=1)

        self._seccion(tarjeta, "CASO", 0)
        self.combo_casos = ttk.Combobox(
            tarjeta, textvariable=self.caso_actual, values=list(self.casos),
            state="readonly", width=26,
        )
        self.combo_casos.grid(row=1, column=0, sticky="ew")
        self.combo_casos.bind("<<ComboboxSelected>>", self._al_elegir)

        self._seccion(tarjeta, "MÉTODO A MOSTRAR", 2, arriba=10)
        self.combo_tecnicas = ttk.Combobox(
            tarjeta, textvariable=self.tecnica_actual,
            values=[nombre for nombre, _ in self.tecnicas], state="readonly", width=26,
        )
        self.combo_tecnicas.grid(row=3, column=0, sticky="ew")
        self.combo_tecnicas.bind("<<ComboboxSelected>>", self._al_elegir)

        ttk.Separator(tarjeta).grid(row=4, column=0, sticky="ew", pady=12)

        self._seccion(tarjeta, "MÉTODOS A COMPARAR", 5)
        for indice, (nombre, _) in enumerate(self.tecnicas):
            ttk.Checkbutton(
                tarjeta, text=nombre, variable=self.seleccion[nombre], style="Tarjeta.TCheckbutton",
            ).grid(row=6 + indice, column=0, sticky="w")
        fila = 6 + len(self.tecnicas)

        self.boton = ttk.Button(
            tarjeta, text="Comparar métodos", style="Acento.TButton",
            command=self._iniciar_comparacion, cursor="hand2",
        )
        self.boton.grid(row=fila, column=0, sticky="ew", pady=(12, 8))
        self.progreso = ttk.Progressbar(tarjeta, mode="determinate", maximum=1, value=0)
        self.progreso.grid(row=fila + 1, column=0, sticky="ew")
        ttk.Label(
            tarjeta, textvariable=self.estado_texto, style="TarjetaSuave.TLabel",
            wraplength=240, justify="left",
        ).grid(row=fila + 2, column=0, sticky="w", pady=(5, 0))

        return tarjeta

    def _construir_principal(self, padre):
        principal = ttk.Frame(padre)
        principal.columnconfigure(0, weight=1)
        principal.rowconfigure(0, weight=1)

        tableros = ttk.Frame(principal)
        tableros.grid(row=0, column=0, sticky="nsew", pady=(0, 12))
        tableros.columnconfigure((0, 1), weight=1, uniform="tablero")
        tableros.rowconfigure(0, weight=1)
        self.canvas_original = self._panel_tablero(
            tableros, 0, "TABLERO ORIGINAL", self.original_subtitulo
        )
        self.canvas_solucion = self._panel_tablero(
            tableros, 1, "SOLUCIÓN", self.solucion_subtitulo
        )

        self._construir_tabla(principal).grid(row=1, column=0, sticky="ew")
        return principal

    def _panel_tablero(self, padre, columna, titulo, subtitulo):
        tarjeta = self._tarjeta(padre, padx=12, pady=10)
        tarjeta.grid(row=0, column=columna, sticky="nsew", padx=(0, 6) if columna == 0 else (6, 0))
        tarjeta.columnconfigure(0, weight=1)
        tarjeta.rowconfigure(2, weight=1)
        self._seccion(tarjeta, titulo, 0)
        ttk.Label(tarjeta, textvariable=subtitulo, style="TarjetaSuave.TLabel").grid(
            row=1, column=0, sticky="w", pady=(0, 6)
        )
        canvas = TableroCanvas(
            tarjeta, self.fuentes["digito"], self.fuentes["mensaje"], width=240, height=240
        )
        canvas.grid(row=2, column=0, sticky="nsew")
        return canvas

    def _construir_tabla(self, padre):
        c = tema.COLORES
        tarjeta = self._tarjeta(padre, padx=12, pady=10)
        tarjeta.columnconfigure(0, weight=1)
        self._seccion(tarjeta, "RESULTADOS", 0)

        columnas = ("caso", "vacias", "metodo", "tiempo", "resultado")
        self.tabla = ttk.Treeview(
            tarjeta, columns=columnas, show="headings", height=5, selectmode="browse"
        )
        encabezados = {
            "caso": ("Caso", 80, "w"), "vacias": ("Vacías", 60, "e"),
            "metodo": ("Método", 210, "w"), "tiempo": ("Tiempo", 90, "e"),
            "resultado": ("Resultado", 130, "w"),
        }
        for columna, (texto, ancho, anclaje) in encabezados.items():
            self.tabla.heading(columna, text=texto, anchor=anclaje)
            self.tabla.column(
                columna, width=ancho, minwidth=60, anchor=anclaje,
                stretch=columna in ("metodo", "resultado"),
            )
        self.tabla.tag_configure("par", background=c["fila_par"])
        self.tabla.tag_configure("impar", background=c["fila_impar"])
        self.tabla.tag_configure("ok", foreground=c["exito"])
        self.tabla.tag_configure("aviso", foreground=c["aviso"])
        self.tabla.tag_configure("fallo", foreground=c["error"])
        self.tabla.bind("<<TreeviewSelect>>", self._fila_seleccionada)

        barra = ttk.Scrollbar(tarjeta, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=barra.set)
        self.tabla.grid(row=1, column=0, sticky="ew")
        barra.grid(row=1, column=1, sticky="ns")

        self.aviso_tabla = ttk.Label(
            tarjeta, text="Aún no hay resultados. Pulsa «Comparar métodos».",
            style="TarjetaSuave.TLabel",
        )
        self.aviso_tabla.place(in_=self.tabla, relx=0.5, rely=0.55, anchor="center")

        ttk.Label(
            tarjeta,
            text="Haz clic en una fila para ver ese método en el tablero.",
            style="TarjetaSuave.TLabel",
        ).grid(row=2, column=0, sticky="w", pady=(6, 0))
        return tarjeta

    # ---------- qué se muestra ----------

    def _al_elegir(self, evento):
        evento.widget.selection_clear()
        self._mostrar_caso()

    def _buscar_resultado(self, caso, tecnica):
        return next(
            (r for r in self.resultados if r["caso"] == caso and r["tecnica"] == tecnica), None
        )

    @staticmethod
    def _explicar(resultado):
        estado = resultado["estado"]
        if estado == "no ejecutado":
            return resultado["detalle"].capitalize()
        mensajes = {
            "sin solución": "El método no llegó a una solución completa.",
            "excedió límite": "Se alcanzó el límite de cálculo antes de terminar.",
            "SOLUCIÓN INVÁLIDA": "El método devolvió una solución inválida.",
            "ERROR": "El método falló al ejecutarse.",
        }
        texto = mensajes.get(estado, estado)
        if resultado["detalle"] and resultado["detalle"] != "sin estadísticas":
            texto += f"\n{resultado['detalle']}"
        return texto

    def _mostrar_caso(self):
        caso = self.caso_actual.get()
        tecnica = self.tecnica_actual.get()
        original = self.casos[caso]
        vacias = contar_vacias(original)

        self.original_subtitulo.set(f"{caso} · {vacias} celdas vacías · {81 - vacias} pistas")
        self.canvas_original.mostrar(original)

        resultado = self._buscar_resultado(caso, tecnica)
        if resultado is None:
            self.canvas_solucion.mostrar_mensaje(
                "Pulsa «Comparar métodos» para ver la solución de este método."
            )
            self.solucion_subtitulo.set(f"{tecnica} · sin ejecutar")
        elif resultado["solucion"] is not None:
            self.canvas_solucion.mostrar(resultado["solucion"], original)
            self.solucion_subtitulo.set(
                f"{tecnica} · {ETIQUETAS_ESTADO[resultado['estado']]} · "
                f"{formato_tiempo(resultado['tiempo_s'])}"
            )
        else:
            self.canvas_solucion.mostrar_mensaje(self._explicar(resultado))
            self.solucion_subtitulo.set(
                f"{tecnica} · {ETIQUETAS_ESTADO.get(resultado['estado'], resultado['estado'])}"
            )
        self._actualizar_resumen()

    def _actualizar_resumen(self):
        if not self.resultados:
            for variable in (self.mas_rapido_valor, self.cobertura_valor):
                variable.set("—")
            self.mas_rapido_detalle.set("Compara los métodos para ver el resumen")
            self.cobertura_detalle.set("")
            return

        caso = self.caso_actual.get()
        validos_caso = [r for r in self.resultados if r["caso"] == caso and r["estado"] == "OK"]
        if validos_caso:
            mejor = min(validos_caso, key=lambda r: r["tiempo_s"])
            self.mas_rapido_valor.set(mejor["tecnica"])
            self.mas_rapido_detalle.set(f"{caso} · {formato_tiempo(mejor['tiempo_s'])}")
        else:
            self.mas_rapido_valor.set("Ninguno")
            self.mas_rapido_detalle.set(f"Ningún método resolvió «{caso}»")

        por_tecnica = {}
        for r in self.resultados:
            if r["estado"] == "OK":
                por_tecnica.setdefault(r["tecnica"], []).append(r["tiempo_s"])
        if por_tecnica:
            nombre, tiempos = min(
                por_tecnica.items(), key=lambda par: (-len(par[1]), sum(par[1]) / len(par[1]))
            )
            self.cobertura_valor.set(nombre)
            self.cobertura_detalle.set(
                f"{len(tiempos)}/{len(self.casos)} casos · "
                f"prom. {formato_tiempo(sum(tiempos) / len(tiempos))}"
            )
        else:
            self.cobertura_valor.set("Ninguno")
            self.cobertura_detalle.set("Ningún método resolvió un caso")

    # ---------- comparación en segundo plano ----------

    def _iniciar_comparacion(self):
        seleccionadas = [(n, f) for n, f in self.tecnicas if self.seleccion[n].get()]
        if not seleccionadas:
            messagebox.showwarning(
                "Sin métodos", "Selecciona al menos un método para comparar.", parent=self.root
            )
            return

        self.boton.configure(state="disabled", text="Comparando…")
        self.progreso.configure(value=0, maximum=len(self.casos) * len(seleccionadas))
        self.estado_texto.set("Preparando…")
        threading.Thread(target=self._trabajar, args=(seleccionadas,), daemon=True).start()
        self.root.after(100, self._revisar_cola)

    def _trabajar(self, tecnicas):
        """Se ejecuta en otro hilo; solo se comunica con la ventana a través de la cola."""
        def avanzar(hechas, total, caso, etiqueta):
            self.cola.put(("progreso", hechas, total, caso, etiqueta))

        try:
            resultados = comparar(self.casos, tecnicas, avanzar)
        except Exception as error:
            logger.exception("La comparación falló")
            self.cola.put(("error", f"{type(error).__name__}: {error}"))
        else:
            self.cola.put(("fin", resultados))

    def _revisar_cola(self):
        terminado = False
        try:
            while True:
                mensaje = self.cola.get_nowait()
                if mensaje[0] == "progreso":
                    _, hechas, total, caso, etiqueta = mensaje
                    self.progreso.configure(value=hechas)
                    self.estado_texto.set(f"{hechas + 1}/{total} · {etiqueta} en «{caso}»")
                elif mensaje[0] == "fin":
                    self._terminar(mensaje[1])
                    terminado = True
                else:
                    self._fallar(mensaje[1])
                    terminado = True
        except queue.Empty:
            pass
        if not terminado:
            self.root.after(100, self._revisar_cola)

    def _terminar(self, resultados):
        self.resultados = resultados
        self.boton.configure(state="normal", text="Comparar métodos")
        self.progreso.configure(value=self.progreso.cget("maximum"))
        self.estado_texto.set(f"Listo: {len(resultados)} ejecuciones.")
        self._actualizar_tabla()
        self._mostrar_caso()

    def _fallar(self, texto):
        self.boton.configure(state="normal", text="Comparar métodos")
        self.estado_texto.set("La comparación falló.")
        messagebox.showerror("Error", texto, parent=self.root)

    def _actualizar_tabla(self):
        self.aviso_tabla.place_forget()
        self.tabla.delete(*self.tabla.get_children())
        for indice, r in enumerate(self.resultados):
            self.tabla.insert(
                "", "end",
                values=(
                    r["caso"], r["vacias"], r["tecnica"], formato_tiempo(r["tiempo_s"]),
                    ETIQUETAS_ESTADO.get(r["estado"], r["estado"]),
                ),
                tags=(COLOR_ESTADO.get(r["estado"], "fallo"), "par" if indice % 2 == 0 else "impar"),
            )

    def _fila_seleccionada(self, evento):
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        valores = self.tabla.item(seleccion[0], "values")
        self.caso_actual.set(valores[0])
        self.tecnica_actual.set(valores[2])
        self._mostrar_caso()

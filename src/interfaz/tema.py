"""
Aspecto de la interfaz: colores, fuentes y estilos ttk.

Todo lo visual vive aquí. Para cambiar el look (por ejemplo al tema oscuro) basta con
cambiar la línea `COLORES = CLARA` por `COLORES = OSCURA`; la lógica no se toca.
"""
from tkinter import font as tkfont
from tkinter import ttk

CLARA = {
    "fondo": "#F3F5F8",
    "panel": "#FFFFFF",
    "borde": "#D6DCE5",
    "texto": "#1B2430",
    "texto_suave": "#5E6B7B",
    "acento": "#2457D6",
    "acento_hover": "#1B45B0",
    "acento_suave": "#E3EBFD",
    "sobre_acento": "#FFFFFF",
    "exito": "#13734A",
    "aviso": "#8F5F00",
    "error": "#B42318",
    "fila_par": "#FFFFFF",
    "fila_impar": "#F6F8FB",
    "seleccion": "#DCE6FF",
    "celda": "#FFFFFF",
    "celda_resuelta": "#E3EBFD",
    "linea_fina": "#C9D1DC",
    "linea_gruesa": "#1B2430",
    "pista": "#1B2430",
    "resuelta": "#1B45B0",
}

OSCURA = {
    "fondo": "#0F1620",
    "panel": "#172230",
    "borde": "#2C3C50",
    "texto": "#E8EEF6",
    "texto_suave": "#9FB0C4",
    "acento": "#4C8DFF",
    "acento_hover": "#6BA0FF",
    "acento_suave": "#1F3556",
    "sobre_acento": "#08111F",
    "exito": "#4ADE9A",
    "aviso": "#F2C265",
    "error": "#FF8A80",
    "fila_par": "#172230",
    "fila_impar": "#1B2838",
    "seleccion": "#264469",
    "celda": "#1B2838",
    "celda_resuelta": "#1F3556",
    "linea_fina": "#33465C",
    "linea_gruesa": "#9FB0C4",
    "pista": "#E8EEF6",
    "resuelta": "#8DB8FF",
}

COLORES = CLARA

FAMILIAS_PREFERIDAS = ("Segoe UI", "SF Pro Text", "Helvetica Neue", "Arial", "DejaVu Sans")


def crear_fuentes(root):
    """Crea las fuentes de la app con la primera familia disponible del sistema."""
    disponibles = set(tkfont.families(root))
    familia = next((f for f in FAMILIAS_PREFERIDAS if f in disponibles), "TkDefaultFont")
    return {
        "normal": tkfont.Font(root, family=familia, size=10),
        "negrita": tkfont.Font(root, family=familia, size=10, weight="bold"),
        "pequena": tkfont.Font(root, family=familia, size=9),
        "etiqueta": tkfont.Font(root, family=familia, size=9, weight="bold"),
        "titulo": tkfont.Font(root, family=familia, size=18, weight="bold"),
        "metrica": tkfont.Font(root, family=familia, size=11, weight="bold"),
        "digito": tkfont.Font(root, family=familia, size=16, weight="bold"),
        "mensaje": tkfont.Font(root, family=familia, size=11),
    }


def configurar_estilos(root, fuentes):
    """Aplica los colores y fuentes a los widgets ttk."""
    c = COLORES
    estilo = ttk.Style(root)
    estilo.theme_use("clam")

    root.configure(bg=c["fondo"])
    root.option_add("*TCombobox*Listbox.background", c["panel"])
    root.option_add("*TCombobox*Listbox.foreground", c["texto"])
    root.option_add("*TCombobox*Listbox.selectBackground", c["seleccion"])
    root.option_add("*TCombobox*Listbox.selectForeground", c["texto"])
    root.option_add("*TCombobox*Listbox.font", fuentes["normal"])

    estilo.configure(".", background=c["fondo"], foreground=c["texto"], font=fuentes["normal"],
                     bordercolor=c["borde"], focuscolor=c["fondo"])

    estilo.configure("TFrame", background=c["fondo"])
    estilo.configure("Tarjeta.TFrame", background=c["panel"])

    estilo.configure("TLabel", background=c["fondo"], foreground=c["texto"])
    estilo.configure("Titulo.TLabel", font=fuentes["titulo"])
    estilo.configure("Suave.TLabel", foreground=c["texto_suave"], font=fuentes["pequena"])
    estilo.configure("Tarjeta.TLabel", background=c["panel"])
    estilo.configure("TarjetaSuave.TLabel", background=c["panel"], foreground=c["texto_suave"],
                     font=fuentes["pequena"])
    estilo.configure("Seccion.TLabel", background=c["panel"], foreground=c["texto_suave"],
                     font=fuentes["etiqueta"])
    estilo.configure("Metrica.TLabel", background=c["panel"], foreground=c["texto"],
                     font=fuentes["metrica"])
    estilo.configure("MetricaAcento.TLabel", background=c["panel"], foreground=c["acento"],
                     font=fuentes["metrica"])

    estilo.configure("Tarjeta.TCheckbutton", background=c["panel"], foreground=c["texto"],
                     indicatorbackground=c["panel"], indicatorforeground=c["acento"],
                     upperbordercolor=c["borde"], lowerbordercolor=c["borde"],
                     padding=(2, 3))
    estilo.map("Tarjeta.TCheckbutton",
               background=[("active", c["panel"])],
               indicatorbackground=[("selected", c["acento"]), ("active", c["acento_suave"])],
               indicatorforeground=[("selected", c["sobre_acento"])])

    estilo.configure("TCombobox", fieldbackground=c["panel"], background=c["panel"],
                     foreground=c["texto"], arrowcolor=c["texto_suave"], bordercolor=c["borde"],
                     lightcolor=c["panel"], darkcolor=c["panel"], padding=5)
    estilo.map("TCombobox",
               fieldbackground=[("readonly", c["panel"])],
               foreground=[("readonly", c["texto"])],
               bordercolor=[("focus", c["acento"])])

    estilo.configure("Acento.TButton", background=c["acento"], foreground=c["sobre_acento"],
                     font=fuentes["negrita"], padding=(14, 8), borderwidth=0, relief="flat")
    estilo.map("Acento.TButton",
               background=[("disabled", c["borde"]), ("active", c["acento_hover"])],
               foreground=[("disabled", c["texto_suave"])])

    estilo.configure("Treeview", background=c["panel"], fieldbackground=c["panel"],
                     foreground=c["texto"], rowheight=26, borderwidth=0, font=fuentes["normal"])
    estilo.map("Treeview",
               background=[("selected", c["seleccion"])],
               foreground=[("selected", c["texto"])])
    estilo.configure("Treeview.Heading", background=c["fondo"], foreground=c["texto_suave"],
                     font=fuentes["etiqueta"], padding=(8, 6), relief="flat", borderwidth=0)
    estilo.map("Treeview.Heading", background=[("active", c["fondo"])])

    estilo.configure("TSeparator", background=c["borde"])
    estilo.configure("TScrollbar", background=c["borde"], troughcolor=c["panel"],
                     bordercolor=c["panel"], arrowcolor=c["texto_suave"], relief="flat")
    estilo.configure("Horizontal.TProgressbar", troughcolor=c["fondo"], background=c["acento"],
                     bordercolor=c["fondo"], lightcolor=c["acento"], darkcolor=c["acento"],
                     thickness=6)

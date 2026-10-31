"""Punto de entrada de la interfaz gráfica:  python src/main.py"""
import tkinter as tk
from tkinter import messagebox

from interfaz.app import SudokuApp
from utils import cargar_tablero, listar_casos


def cargar_casos():
    return {nombre: cargar_tablero(ruta) for nombre, ruta in listar_casos()}


def main():
    root = tk.Tk()
    root.withdraw()  # evita una ventana vacía si hay que mostrar un error
    try:
        casos = cargar_casos()
    except (OSError, ValueError) as error:
        messagebox.showerror("No se pudieron leer los casos", str(error), parent=root)
        return
    if not casos:
        messagebox.showerror(
            "Sin casos",
            "No hay archivos caso_*.txt en la carpeta datos/.\n"
            "Ejecuta primero: python src/generar_datos.py",
            parent=root,
        )
        return

    SudokuApp(root, casos)
    root.deiconify()
    root.mainloop()


if __name__ == "__main__":
    main()

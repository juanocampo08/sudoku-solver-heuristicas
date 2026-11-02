# Trabajo final — Sudoku (Análisis y Diseño de Algoritmos 2026-2)

Solver de Sudoku comparando técnicas algorítmicas.

## Estructura
- `datos/`: casos de prueba (`0` = celda vacía). `pequeno` (5 vacías), `mediano` (40), `grande` (55), `extremo` (64, 17 pistas).
- `src/backtracking.py`: backtracking con orden fijo y heurística MRV.
- `src/greedy.py`: resolución voraz sin retroceso.
- `src/divide_y_venceras.py`: descomposición en bandas horizontales.
- `src/programacion_dinamica.py`: resolución fila por fila con memoización.
- `src/generar_datos.py`: crea un nuevo conjunto aleatorio de sudokus, conserva las categorías y cantidades de celdas vacías, y registra la semilla usada en los archivos.
- `src/comparativa.py`: ejecuta los algoritmos disponibles, imprime la tabla y guarda `docs/resultados.json` y, si está instalado matplotlib, `docs/comparativa.png`. La interfaz reutiliza sus funciones `comparar` y `ejecutar_tecnica`.
- `src/main.py`: punto de entrada de la interfaz gráfica (solo arranca la ventana).
- `src/interfaz/`: la interfaz, separada por responsabilidades.
  - `tema.py`: colores (tema claro y oscuro), fuentes y estilos. Es el único lugar donde se cambia el aspecto.
  - `tablero_widget.py`: dibuja el tablero 9x9 y se adapta al tamaño de la ventana.
  - `app.py`: organiza la ventana y conecta los botones con la comparación.

Los solucionadores validan el tablero de entrada y una solución solo se considera correcta
si está completa, no tiene conflictos y respeta las pistas originales.
La comparativa limita backtracking de orden fijo a 100 000 nodos, divide y vencerás a
100 000 combinaciones y programación dinámica a 10 000 estados; los límites se reportan
como tales y evitan que un caso difícil deje la ejecución sin terminar.
Divide y vencerás y programación dinámica se omiten en tableros con más de 55 celdas vacías,
porque la generación de permutaciones por fila puede resultar muy costosa. Los casos con más
de 40 celdas vacías se ejecutan una vez para reducir el tiempo total de la comparativa.

## Uso (Python 3.10+)
```
python src/main.py
python src/comparativa.py
```

La interfaz gráfica usa Tkinter (incluido normalmente con Python). Selecciona uno o varios
métodos y pulsa **Evaluar métodos seleccionados**. La tabla compara esos métodos en todos los
casos; el selector permite consultar el tablero original y las soluciones de cada caso.
La interfaz informa cuál fue el más rápido para el caso elegido y cuál resolvió más casos
válidamente (desempata por el menor tiempo promedio). Esa recomendación depende de los casos
de prueba y no implica que un método sea el mejor para cualquier Sudoku.

`generar_datos.py` se ejecuta cuando se quiera crear un nuevo conjunto de sudokus. Cada
ejecución elige una semilla aleatoria, genera casos diferentes conservando las categorías y
cantidades de celdas vacías, y sobrescribe los cuatro archivos de `datos/`. La semilla queda
en los comentarios de cada archivo para identificar ese conjunto. No hace falta ejecutarlo
antes de cada resolución: `main.py` lee los sudokus que ya están guardados.

# Taller 1 — Grafo Wikipedia (TopCats)

Este proyecto carga un subconjunto del dataset **wiki-topcats** y construye un grafo dirigido de páginas de Wikipedia. Permite calcular métricas como grados, PageRank y recorridos BFS/DFS.

## Estructura del proyecto

```
.
├─ main.py
├─ dataset/
│  ├─ wiki-topcats.mtx
│  ├─ wiki-topcats_Categories.mtx
│  ├─ wiki-topcats_Category_names.txt
│  └─ wiki-topcats_pagenames.txt
├─ src/
│  ├─ helpers/
│  │  └─ wikipedia.py
│  └─ models/
│     ├─ grafo.py
│     └─ nodo.py
└─ DiagramaTaller1.drawio.png
```

## Requisitos

- Python 3.8+
- No requiere librerías externas.

## Cómo ejecutar

Ejecuta el archivo principal:

```
python main.py
```

El script crea los nodos, construye el grafo, calcula PageRank y muestra el top 3.

## Módulo de grafo (`src/models/grafo.py`)

Clase: `Grafo`

### `__init__(self, nodos)`

- **Parámetros**: `nodos` (dict) — Mapa `id_nodo -> Nodo`.
- **Descripción**: Inicializa el grafo con los nodos cargados.

### `get_grado_entrada(self, id_nodo)`

- **Parámetros**: `id_nodo` (int).
- **Retorna**: `int` — cantidad de enlaces entrantes al nodo.
- **Descripción**: Recorre todos los nodos y cuenta cuántos apuntan a `id_nodo`.

### `get_grado_salida(self, id_nodo)`

- **Parámetros**: `id_nodo` (int).
- **Retorna**: `int` — cantidad de enlaces salientes del nodo.
- **Descripción**: Usa `Nodo.get_links()` para contar enlaces salientes.

### `get_max_links(self, cant_nodos)`

- **Parámetros**: `cant_nodos` (int).
- **Retorna**: `list[tuple]` — lista de tuplas `(cantidad_links, id_nodo)`.
- **Descripción**: Devuelve los `cant_nodos` con más enlaces salientes.

### `get_degree_distribution(self)`

- **Retorna**: `dict` con:
  - `in_degrees`: grados de entrada por nodo.
  - `out_degrees`: grados de salida por nodo.
  - `in_distribution`: distribución de grados de entrada (grado -> cantidad de nodos).
  - `out_distribution`: distribución de grados de salida (grado -> cantidad de nodos).
  - `avg_in_degree`, `avg_out_degree`: promedios.
  - `max_in_degree`, `max_out_degree`: máximos.
- **Descripción**: Calcula métricas globales de grados.

### `dfs(self, start_node_id=None)`

- **Parámetros**: `start_node_id` (int | None).
- **Retorna**: `list[int]` — orden de visita en DFS.
- **Descripción**: Recorrido DFS recursivo desde el nodo indicado. Si es `None`, usa el primer nodo del diccionario.
- **Errores**: `ValueError` si el nodo no existe.

### `bfs(self, start_node_id, finish_node_id)`

- **Parámetros**: `start_node_id` (int), `finish_node_id` (int).
- **Retorna**: `list[int] | None` — camino más corto (lista de ids) o `None` si no hay camino.
- **Descripción**: BFS para encontrar el camino más corto entre dos nodos.
- **Errores**: `ValueError` si algún nodo no existe.

### `pagerank(self, iteraciones)`

- **Parámetros**: `iteraciones` (int).
- **Retorna**: `dict` — `id_nodo -> score`.
- **Descripción**: Calcula PageRank con amortiguación fija `d = 0.85`. Maneja nodos sin enlaces (dangling) redistribuyendo su puntaje.

### `obtener_top_pagerank(self, puntajes_pagerank, top)`

- **Parámetros**: `puntajes_pagerank` (dict), `top` (int).
- **Retorna**: `list[dict]` — lista de elementos con `id`, `titulo`, `score`, `category`.
- **Descripción**: Obtiene el top de nodos según el PageRank calculado.

## Módulo de Wikipedia (`src/helpers/wikipedia.py`)

Clase: `WikipediaLoader`

### `__init__(self, ruta=None)`

- **Parámetros**: `ruta` (str | Path | None).
- **Descripción**: Define la ruta del dataset. Si `ruta` es `None`, usa `dataset/` en la raíz del proyecto.

### `get_data_ruta(self)`

- **Retorna**: `Path` — ruta base del dataset.
- **Descripción**: Devuelve la ruta configurada.

### `nombres_paginas(self)`

- **Retorna**: `dict` — `id_pagina -> nombre`.
- **Descripción**: Lee `wiki-topcats_pagenames.txt` y carga las primeras 199 páginas (ids 1..199).

### `nombres_categorias(self)`

- **Retorna**: `dict` — `id_categoria -> nombre`.
- **Descripción**: Lee `wiki-topcats_Category_names.txt` y carga las primeras 199 categorías (ids 1..199).

### `categoria_por_pagina(self, paginas_cargadas)`

- **Parámetros**: `paginas_cargadas` (dict) — páginas ya cargadas.
- **Retorna**: `dict` — `id_pagina -> [id_categoria, ...]`.
- **Descripción**: Lee `wiki-topcats_Categories.mtx` y asigna categorías solo a las páginas cargadas.

### `crear_nodos(self)`

- **Retorna**: `dict` — `id_pagina -> Nodo`.
- **Descripción**: Crea objetos `Nodo` con nombre y categorías. Si una página no tiene categoría, se asigna lista vacía.

### `cargar_enlaces(self, nodos)`

- **Parámetros**: `nodos` (dict) — nodos existentes.
- **Retorna**: `dict` — nodos con enlaces cargados.
- **Descripción**: Lee `wiki-topcats.mtx` y agrega enlaces salientes entre páginas que existan en el subconjunto.

### `get_nodos(self)`

- **Retorna**: `dict` — nodos listos con enlaces.
- **Descripción**: Orquesta la creación de nodos y la carga de enlaces.

## Modelo de nodo (`src/models/nodo.py`)

Clase: `Nodo`

- **Atributos**:
  - `id` (int): identificador.
  - `pagename` (str): nombre de la página.
  - `categories` (list[str]): categorías.
  - `links` (list[int]): ids de nodos destino.

### `get_links(self)`

- **Retorna**: `list[int]` — enlaces salientes.

### `get_categories(self)`

- **Retorna**: `list[str]` — categorías del nodo.

## Ejemplo de uso mínimo

```python
from src.helpers.wikipedia import WikipediaLoader
from src.models.grafo import Grafo

wiki = WikipediaLoader()
nodos = wiki.get_nodos()

grafo = Grafo(nodos)

print(grafo.get_grado_entrada(1))
print(grafo.get_grado_salida(1))
print(grafo.get_max_links(5))
print(grafo.get_degree_distribution())
print(grafo.dfs(1))
print(grafo.bfs(1, 10))

pagerank = grafo.pagerank(20)
print(grafo.obtener_top_pagerank(pagerank, 3))
```

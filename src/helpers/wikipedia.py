from pathlib import Path
from src.models.nodo import Nodo


class WikipediaLoader:
    def __init__(self, ruta=None):
        if ruta is None:
            self.ruta_dataset = Path(__file__).resolve(
            ).parent.parent.parent / "dataset"
        else:
            self.ruta_dataset = Path(ruta)

    def get_data_ruta(self):
        return self.ruta_dataset

    def nombres_paginas(self):
        ruta = self.ruta_dataset / "wiki-topcats_pagenames.txt"
        nombres = {}
        with open(ruta, "r", encoding="utf-8") as archivo:
            index = 1
            for linea in archivo:
                if (index < 200):
                    nombres[index] = linea.strip()
                index += 1
        return nombres

    def nombres_categorias(self):
        ruta = self.ruta_dataset / "wiki-topcats_Category_names.txt"
        categorias = {}
        with open(ruta, "r", encoding="utf-8") as archivo:
            # Cargamos las primeras 2000 para tener de donde elegir
            for i, linea in enumerate(archivo):
                if i >= 2000:
                    break
                categorias[i + 1] = linea.strip()
        return categorias

    def categoria_por_pagina(self, paginas_cargadas):
        ruta = self.ruta_dataset / "wiki-topcats_Categories.mtx"
        pagina_categoria = {}

        index = 0

        with open(ruta, "r", encoding="utf-8") as archivo:
            linea = archivo.readline()
            while (linea.startswith("%")):
                linea = archivo.readline()

            for linea in archivo:
                partes = linea.strip().split()
                if (len(partes) == 2):

                    id_pag = int(partes[0])
                    id_cat = int(partes[1])
                    if id_pag in paginas_cargadas:
                        if (id_pag not in pagina_categoria):
                            pagina_categoria[id_pag] = [id_cat]

                        else:
                            pagina_categoria[id_pag].append(id_cat)
        return pagina_categoria

    def crear_nodos_por_bloque_categorias(self, limite_nodos=5000):
        nodos = {}
        paginas_seleccionadas = set()
        cat_name = self.nombres_categorias()

        # 1. Mapeo rápido de categorías
        ruta_cat = self.ruta_dataset / "wiki-topcats_Categories.mtx"

        # Usaremos un diccionario temporal para agrupar páginas por categoría
        # Esto nos permite elegir categorías completas
        with open(ruta_cat, "r", encoding="utf-8") as archivo:
            for linea in archivo:
                if linea.startswith("%"):
                    continue
                partes = linea.strip().split()
                if len(partes) >= 2:
                    id_pag = int(partes[0])
                    id_cat = int(partes[1])

                # Solo agregamos si no nos pasamos del límite
                    if len(paginas_seleccionadas) < limite_nodos:
                        paginas_seleccionadas.add(id_pag)
                    else:
                        break

        # 2. Cargar metadatos (Nombres y todas las categorías de esas páginas)
        # Reutilizamos tu lógica de 'nombres_paginas' pero filtrada por nuestro SET
        pag_names_filtrados = {}
        ruta_names = self.ruta_dataset / "wiki-topcats_pagenames.txt"
        with open(ruta_names, "r", encoding="utf-8") as archivo:
            for i, linea in enumerate(archivo):
                id_actual = i + 1
                if id_actual in paginas_seleccionadas:
                    pag_names_filtrados[id_actual] = linea.strip()

        # Obtenemos TODAS las categorías de las páginas que ya decidimos trackear
        cat_pag = self.categoria_por_pagina(paginas_seleccionadas)

        # 3. Construcción de objetos Nodo
        for id_pag in paginas_seleccionadas:
            nombre = pag_names_filtrados.get(id_pag, f"Pagina_{id_pag}")
            # Buscamos los nombres de las categorías de este nodo
            categorias_nodo = [cat_name.get(
                c, f"Cat_{c}") for c in cat_pag.get(id_pag, [])]
            nodos[id_pag] = Nodo(nombre, id_pag, categorias_nodo)

        return nodos

    def cargar_enlaces(self, nodos):
        ruta = self.ruta_dataset / "wiki-topcats.mtx"

        with open(ruta, "r", encoding="utf-8") as archivo:
            linea = archivo.readline()
            while (linea.startswith("%")):
                linea = archivo.readline()

            for linea in archivo:
                partes = linea.strip().split()

                id_origen = int(partes[0])
                id_destino = int(partes[1])

                nodo_origen = nodos.get(id_origen)
                # lineas proteccion al filtrado de <200.
                if nodo_origen is not None:
                    if id_destino in nodos:
                        nodo_origen.links.append(id_destino)

        return nodos

    def get_nodos(self, limite_nodos=5000):
        # 1. Filtra y crea nodos que pertenecen a las primeras categorías del dataset
        nodos_filtrados = self.crear_nodos_por_bloque_categorias(limite_nodos)
        # 2. Solo inyecta los links que conectan a esos 1000 entre sí
        nodos_con_links = self.cargar_enlaces(nodos_filtrados)
        return nodos_con_links

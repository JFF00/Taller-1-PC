import heapq
from collections import deque
from src.models.nodo import Nodo


class Grafo:
    def __init__(self, nodos):
        self.nodos = nodos

    # Funcion que busca la cantidad de entradas para un id de nodo.
    def get_grado_entrada(self, id_nodo):
        entries = 0
        nodos = self.nodos
        for nodo in nodos.values():
            for link in nodo.links:
                if link == id_nodo:
                    entries += 1
        return entries

    def get_grado_salida(self, id_nodo):
        nodos = self.nodos
        outs = len(nodos[id_nodo].get_links())
        return outs

    def get_max_links(self, cant_nodos):
        # Retorna el top tamaño:cant_nodos de nodos con mas links hacia afuera
        nodes_with_counts = [(len(nodo.get_links()), nodo_id)
                             for nodo_id, nodo in self.nodos.items()]

        top_nodes = heapq.nlargest(cant_nodos, nodes_with_counts)

        # Return es una tupla del id y la cantidad de links
        return top_nodes

    def get_degree_distribution(self):

        in_degrees = {}
        out_degrees = {}

        # Calculate all in-degrees and out-degrees
        for node_id in self.nodos:
            out_degrees[node_id] = self.get_grado_salida(node_id)
            in_degrees[node_id] = self.get_grado_entrada(node_id)

        # Distribution counts (how many nodes have degree k)
        out_dist = {}
        in_dist = {}

        for degree in out_degrees.values():
            out_dist[degree] = out_dist.get(degree, 0) + 1

        for degree in in_degrees.values():
            in_dist[degree] = in_dist.get(degree, 0) + 1

        return {
            'in_degrees': in_degrees,
            'out_degrees': out_degrees,
            'in_distribution': in_dist,  # degree -> count
            'out_distribution': out_dist,
            'avg_in_degree': sum(in_degrees.values()) / len(in_degrees) if in_degrees else 0,
            'avg_out_degree': sum(out_degrees.values()) / len(out_degrees) if out_degrees else 0,
            'max_in_degree': max(in_degrees.values()) if in_degrees else 0,
            'max_out_degree': max(out_degrees.values()) if out_degrees else 0,
        }

    def dfs(self, start_node_id=None):

        if not self.nodos:
            return []

        if start_node_id is None:
            start_node_id = next(iter(self.nodos.keys()))

        if start_node_id not in self.nodos:
            raise ValueError(
                f"Nodo {start_node_id} no se encuentra en el grafo")

        visited = set()
        result = []

        def _dfs_recursive(node_id):
            visited.add(node_id)
            result.append(node_id)

            # Explora los vecinos, es decir links hacia afuera.
            for neighbor_id in self.nodos[node_id].get_links():
                if neighbor_id not in visited and neighbor_id in self.nodos:
                    _dfs_recursive(neighbor_id)

        _dfs_recursive(start_node_id)
        return result

    def bfs(self, start_node_id, finish_node_id):
        # Función que ejecuta el BFS y retorna el camino más corto entre los dos nodos dados.

        if start_node_id not in self.nodos:
            raise ValueError(
                f"Nodo inicial {start_node_id} no se encuentra en el grafo")
        if finish_node_id not in self.nodos:
            raise ValueError(
                f"Nodo final {finish_node_id} no se encuentra en el grafo")

        # Si los nodos son iguales, el camino es trivial
        if start_node_id == finish_node_id:
            return [start_node_id]

        # Inicializamos la cola con el nodo inicial
        cola = deque([start_node_id])
        visitados = {start_node_id}
        # Diccionario para rastrear el camino: nodo_actual -> nodo_anterior
        padres = {start_node_id: None}

        while cola:
            nodo_actual = cola.popleft()

            # Exploramos todos los vecinos (enlaces salientes)
            for vecino_id in self.nodos[nodo_actual].get_links():
                # Si encontramos el nodo destino, reconstruimos el camino
                if vecino_id == finish_node_id:
                    # Reconstruir camino desde el destino hasta el inicio
                    camino = [finish_node_id]
                    padres[vecino_id] = nodo_actual
                    nodo = vecino_id
                    while nodo is not None:
                        camino.append(nodo)
                        nodo = padres[nodo]
                    return camino[::-1]  # Invertir para obtener inicio -> fin

                # Si no hemos visitado el vecino, lo agregamos a la cola
                if vecino_id not in visitados and vecino_id in self.nodos:
                    visitados.add(vecino_id)
                    padres[vecino_id] = nodo_actual
                    cola.append(vecino_id)

        # Si llegamos aquí, no hay camino entre los nodos
        return None

    def pagerank(self, iteraciones, d=0.85):
        """ 
        Iteraciones y grado de amortiguación(d) están parametrizados.
        d=0.85 se utiliza normalmente este valor para quitar peso a las páginas y evitar que páginas sin peso se beneficien.
        iteraciones=20
        """
        n = len(self.nodos)
        puntaje_inicial = 1.0 / n
        nodos_puntajes_iniciales = dict.fromkeys(self.nodos, puntaje_inicial)
        for i in range(iteraciones):
            nodos_puntajes_aux = dict.fromkeys(self.nodos, (1-d)/n)
            suma_dangling = 0
            # busqueda de nodos sin vecinos
            for id in nodos_puntajes_iniciales:
                if self.nodos[id].links == []:
                    suma_dangling += nodos_puntajes_iniciales[id]
            bono = (d * suma_dangling) / n
            # suma del bono de nodos sin vecinos a los demás
            for id in nodos_puntajes_aux:
                nodos_puntajes_aux[id] += bono

            # busqueda de nodos con vecinos y suma de votos
            for id in nodos_puntajes_iniciales:
                vecinos = self.nodos[id].links
                if vecinos:
                    puntaje_aux = (
                        nodos_puntajes_iniciales[id] / len(vecinos)) * d
                    for vecino in vecinos:
                        if vecino in nodos_puntajes_aux:
                            nodos_puntajes_aux[vecino] += puntaje_aux

            # reemplazo valores
            nodos_puntajes_iniciales = nodos_puntajes_aux

        return nodos_puntajes_iniciales

    def obtener_top_pagerank(self, puntajes_pagerank, top):
        """
        función que obtiene el top del dict generado en pagerank
        """
        top_ids = heapq.nlargest(top, puntajes_pagerank,
                                 key=puntajes_pagerank.get)

        ranking = []
        for id in top_ids:
            nodo = self.nodos[id]
            score = puntajes_pagerank[id]

            ranking.append({
                "id": id,
                "titulo": nodo.pagename,
                "score": score,
                "category": nodo.categories
            })

        return ranking

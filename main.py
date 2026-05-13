from src.helpers.wikipedia import WikipediaLoader
from src.models.nodo import Nodo
from src.models.grafo import Grafo

wiki = WikipediaLoader()
nodos = wiki.get_nodos()
grafo = Grafo(nodos)
pagerank = grafo.pagerank(35)
# print(grafo.get_max_links(3))
print(grafo.obtener_top_pagerank(pagerank, 3))

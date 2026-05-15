from pathlib import Path
import csv
import time
from collections import Counter

from src.helpers.wikipedia import WikipediaLoader
from src.models.grafo import Grafo


def guardar_csv(path, encabezados, filas):
    with open(path, "w", newline="", encoding="utf-8") as archivo:
        writer = csv.writer(archivo)
        writer.writerow(encabezados)
        writer.writerows(filas)


def main():
    inicio = time.perf_counter()

    wiki = WikipediaLoader()
    nodos = wiki.get_nodos(5000)
    grafo = Grafo(nodos)

    output_dir = Path(__file__).resolve().parent / "outputs"
    output_dir.mkdir(exist_ok=True)

    # 4.3 Métricas básicas
    degree_stats = grafo.get_degree_distribution()
    top_out = grafo.get_max_links(10)
    top_in = sorted(
        degree_stats["in_degrees"].items(), key=lambda item: item[1], reverse=True
    )[:10]

    # 4.4 Recorrido del grafo (DFS/BFS)
    dfs_recorrido = grafo.dfs()
    if len(dfs_recorrido) >= 2:
        start_id = dfs_recorrido[0]
        end_id = dfs_recorrido[1]
    else:
        start_id = dfs_recorrido[0]
        end_id = dfs_recorrido[0]

    bfs_camino = grafo.bfs(start_id, end_id)
    conectado = bfs_camino is not None

    # 4.5 PageRank (versión simplificada)
    iteraciones = 35
    amortiguacion = 0.85
    pagerank = grafo.pagerank(iteraciones, amortiguacion)
    top_pagerank = grafo.obtener_top_pagerank(pagerank, 10)

    # 4.6 Análisis de resultados
    categorias_top = Counter()
    for item in top_pagerank:
        for cat in item["category"]:
            categorias_top[cat] += 1

    ratio_in = (
        degree_stats["max_in_degree"] / degree_stats["avg_in_degree"]
        if degree_stats["avg_in_degree"] else 0
    )
    ratio_out = (
        degree_stats["max_out_degree"] / degree_stats["avg_out_degree"]
        if degree_stats["avg_out_degree"] else 0
    )
    top_in_ids = {node_id for node_id, _ in top_in}
    top_pr_ids = {item["id"] for item in top_pagerank}
    overlap = len(top_in_ids & top_pr_ids)
    top_cat = categorias_top.most_common(1)
    top_cat_text = (
        f"{top_cat[0][0]} ({top_cat[0][1]})"
        if top_cat else
        "No hay categorías en el top"
    )

    # Mostrar por consola (claro y resumido)
    print("Top 10 PageRank:")
    for i, item in enumerate(top_pagerank, start=1):
        print(
            f"{i}. {item['titulo']} (id={item['id']}) score={item['score']:.6f}")

    print("\nTop 10 grados de salida:")
    for i, (count, node_id) in enumerate(top_out, start=1):
        print(f"{i}. id={node_id} out_degree={count}")

    print("\nTop 10 grados de entrada:")
    for i, (node_id, count) in enumerate(top_in, start=1):
        print(f"{i}. id={node_id} in_degree={count}")

    print("\nResumen de grados:")
    print(
        f"avg_in={degree_stats['avg_in_degree']:.2f} | "
        f"avg_out={degree_stats['avg_out_degree']:.2f} | "
        f"max_in={degree_stats['max_in_degree']} | "
        f"max_out={degree_stats['max_out_degree']}"
    )

    print("\nRecorridos del grafo:")
    print(f"DFS visitó {len(dfs_recorrido)} nodos")
    if conectado:
        print(
            f"BFS encontró camino entre {start_id} y {end_id} "
            f"(longitud {len(bfs_camino) - 1})"
        )
    else:
        print(f"BFS no encontró camino entre {start_id} y {end_id}")

    # Archivos (rankings y tablas)
    guardar_csv(
        output_dir / "top_pagerank.csv",
        ["rank", "id", "titulo", "score", "categorias"],
        [
            [i, item["id"], item["titulo"], f"{item['score']:.6f}",
             "; ".join(item["category"])]
            for i, item in enumerate(top_pagerank, start=1)
        ],
    )

    guardar_csv(
        output_dir / "top_out_degree.csv",
        ["rank", "id", "out_degree"],
        [
            [i, node_id, count]
            for i, (count, node_id) in enumerate(top_out, start=1)
        ],
    )

    guardar_csv(
        output_dir / "top_in_degree.csv",
        ["rank", "id", "in_degree"],
        [
            [i, node_id, count]
            for i, (node_id, count) in enumerate(top_in, start=1)
        ],
    )

    guardar_csv(
        output_dir / "degree_distribution.csv",
        ["degree", "in_count", "out_count"],
        [
            [
                degree,
                degree_stats["in_distribution"].get(degree, 0),
                degree_stats["out_distribution"].get(degree, 0),
            ]
            for degree in sorted(
                set(degree_stats["in_distribution"]) |
                set(degree_stats["out_distribution"])
            )
        ],
    )

    guardar_csv(
        output_dir / "top_categories_pagerank.csv",
        ["categoria", "frecuencia"],
        categorias_top.most_common(),
    )

    # Interpretación mínima en archivo resumen
    resumen = [
        "Resumen de análisis",
        f"Total nodos: {len(nodos)}",
        f"Avg in-degree: {degree_stats['avg_in_degree']:.2f}",
        f"Avg out-degree: {degree_stats['avg_out_degree']:.2f}",
        f"Max in-degree: {degree_stats['max_in_degree']}",
        f"Max out-degree: {degree_stats['max_out_degree']}",
        f"DFS visitó: {len(dfs_recorrido)} nodos",
        (
            f"BFS camino {start_id}->{end_id}: {len(bfs_camino) - 1}"
            if conectado else
            f"BFS sin camino {start_id}->{end_id}"
        ),
        "\nPatrones observados:",
        (
            f"- Concentración de enlaces: max/avg in-degree={ratio_in:.1f}, "
            f"max/avg out-degree={ratio_out:.1f}."
        ),
        f"- Coincidencia PageRank vs in-degree: {overlap}/10 nodos.",
        f"- Categoría dominante en el Top PageRank: {top_cat_text}.",
    ]
    with open(output_dir / "resumen.txt", "w", encoding="utf-8") as archivo:
        archivo.write("\n".join(resumen))

    fin = time.perf_counter()
    print(f"\nTiempo total de ejecución: {fin - inicio:.2f} s")


if __name__ == "__main__":
    main()

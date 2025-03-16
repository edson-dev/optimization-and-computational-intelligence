import networkx as nx
import hashlib
import matplotlib.pyplot as plt

def img(ord, graph)-> str:
    g = nx.DiGraph()

    #ord = ['lung', 'tub', 'smoke', 'bronc', 'either', 'xray', 'dysp']
    #graph = [('lung', 'smoke'), ('lung', 'either'), ('tub', 'either'), ('smoke', 'bronc'), ('bronc', 'dysp'),
    #         ('either', 'xray'), ('either', 'dysp')]

    g.add_nodes_from(ord)
    g.add_edges_from(graph)
    file = f'dag/{hashlib.md5(str(graph).encode('utf-8')).hexdigest()}.png'
    nx.draw(g, node_color=["red" if node == ord[0] else "blue" for node in g], with_labels=True, width=2,
            node_size=1200)
    # plt.show()
    plt.savefig(file, bbox_inches='tight')
    return file
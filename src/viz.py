import networkx as nx
import hashlib
import matplotlib.pyplot as plt

def file(ord, graph)-> str:
    g = nx.DiGraph()

    for i in ord:
        if i in str(graph):
            continue
        else:
            ord.remove(i)
    g.add_nodes_from(ord)
    g.add_edges_from(graph)
    file = f'dag/{hashlib.md5(str(graph).encode('utf-8')).hexdigest()}.png'
    nx.draw(g, node_color=["red" if node == ord[0] else "blue" for node in g], with_labels=True, width=2,
            node_size=1200)
    # plt.show()
    plt.savefig(file, bbox_inches='tight')
    return file

if __name__ == "__main__":
    ord = ['lung', 'tub', 'smoke', 'bronc', 'either', 'xray', 'dysp'] # str(list(best_model))
    graph = [('lung', 'smoke'), ('lung', 'either'), ('tub', 'either'), ('smoke', 'bronc'), ('bronc', 'dysp'), #str(best_model.edges)
             ('either', 'xray'), ('either', 'dysp')]
    file(ord,graph)
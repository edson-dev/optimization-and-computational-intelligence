from sql import RepositorySQL
from pgmpy.readwrite import XMLBIFReader


def count_edges(base, alg,art:str,comp:str, db:RepositorySQL = RepositorySQL("sqlite:///./networks.db")):
    c, a, m, rs = 0, 0, 0, 0
    art = XMLBIFReader(string=art)
    result = XMLBIFReader(string=comp)
    #print("art:", art.get_edges())
    #print("result:", result.get_edges())
    for i in result.get_edges():
        rv = i[::-1]
        edges = art.get_edges()
        if i in edges:
            c += 1
        else:
            a += 1
        if rv in edges:
            rs += 1
    for i in art.get_edges():
            edges = result.get_edges()
            if i not in edges:
                m += 1
    response = {
        "base": base,
        "algorithm": alg,
        "correct": c,
        "additional": a,
        "missing": m,
        "reverse": rs,
        "accuracy": (c / (c + a + m + rs))
    }
    print(response)
    with db as repo:
        a = repo.upsert("optimization", response, keys=["algorithm", "base"])


if __name__ == "__main__":
    from main import exec_bases, alg
    bases = ["asia"]
    alg = ["pearson"]
    for i in bases:
        for j in alg:
            count_edges(i, j,open(f"bif/{i}.xml.bif").read(),open(f"result/{i}_{j}.xml.bif").read())

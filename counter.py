base = "asia"
alg = "boruta"
base_file = f"bif/{base}.xmlbif"
file_path = f"result/{base}_{alg}_best.xmlbif"
from pgmpy.readwrite import XMLBIFReader

if __name__ == "__main__":
    c,a,m,rs = 0,0,0,0

    b = XMLBIFReader(base_file)
    r = XMLBIFReader(file_path)

    print("base:",b.get_edges())
    print("resource:",r.get_edges())
    for i in r.get_edges():
        rv = [i[1],i[0]]
        edges =  b.get_edges()
        if i in edges:
            c+=1
        else:
            m+=1
        if i not in edges:
            a+=1
        if rv in edges:
            rs+=1
    result = {
        "base": base,
        "algorithm": alg,
        "correct": c,
        "additional": a,
        "missing": m,
        "reverse": rs,
        "accuracy": (c/(c+a+m+rs))
    }
    print(result)

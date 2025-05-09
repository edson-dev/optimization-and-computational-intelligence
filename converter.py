import os
import time

import pandas as pd
from pgmpy.estimators import K2Score
from pgmpy.readwrite import BIFReader, XMLBIFWriter, XMLBIFReader


from sql import RepositorySQL


def execute(base:str, db:RepositorySQL = RepositorySQL("sqlite:///./networks.db") ):
    # convert file
    start_time = time.time()
    file_name = f"bif/{base}.bif"
    output = f"bif/{base}.xml.bif"
    if not os.path.isfile(output):
        if os.path.isfile(file_name):
            reader = BIFReader(file_name)
            writer = XMLBIFWriter(reader.get_model())
            writer.write_xmlbif(output)
    if not os.path.exists(output):
        raise FileNotFoundError(f"The file '{output}' does not exist.")
    if not os.path.exists(f"data/{base}.csv"):
        raise FileNotFoundError(f"The file {base}.csv does not exist.")
    data = pd.read_csv(f"data/{base}.csv")
    r = XMLBIFReader(output)
    w = XMLBIFWriter(r.get_model())
    model = r.get_model()
    #data.columns = data.columns.str.upper()
    k2 = K2Score(data)
    score = k2.score(model)
    with db as repo:
        d = {"algorithm": "art", "base": base,
             "structure": str(r.get_edges()), "score": float(score), "time": time.time()-start_time,
             "correct": len(r.get_edges()),
             "additional": 0,
             "missing": 0,
             "reverse": 0,
             "accuracy": float(1.0),
             "xmlbif": output, "file": w.__str__()}
        print(d)
        a = repo.upsert("optimization", d, keys=["algorithm", "base"])


if __name__ == "__main__":
    bases = ["asia"]
    for base in bases:
        execute(base)



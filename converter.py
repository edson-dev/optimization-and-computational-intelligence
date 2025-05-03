import pandas as pd
from pgmpy.estimators import K2Score
from pgmpy.readwrite import BIFReader, XMLBIFWriter
import xml.etree.ElementTree as ET

from sql import RepositorySQL


def execute(base:str):
    # convert file
    file_name = f"bif/{base}.bif"
    output = f"bif/{base}.xmlbif"
    reader = BIFReader(file_name)
    writer = XMLBIFWriter(reader.get_model())
    writer.write_xmlbif(output)
    # calculate score
    data = pd.read_csv(f"data/{base}.csv")
    k2 = K2Score(data)
    score = k2.score(reader.get_model())
    print(f"K2 Score: {score}")
    with RepositorySQL("sqlite:///./masters.db") as repo:
        d = {"algorithm": "art", "base": base,
             "structure": str(reader.get_edges()), "score": score, "time": None,
             "xmlbif": output}
        print(d)
        a = repo.upsert("optimization", d, keys=["algorithm", "base"])


if __name__ == "__main__":
    bases = ["asia"]
    for base in bases:
        execute(base)



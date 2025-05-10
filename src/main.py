from counter import count_edges
from converter import execute as conversor
from k2random import execute as random
from k2boruta import execute as boruta
from k2pearson import execute as pearson
from k2spearman import execute as spearman
from k2kendall import execute as kendall
from sql import RepositorySQL

small = ["asia","cancer","earthquake","sachs","survey"]
medium = ["alarm","barley","child","insurance","mildew","water"]
large = ["hailfinder","hepar2","win95pts"]
vlarge = ["andes","diabetes","link","munin1","pathfinder","pigs"]
massive = ["munin"]
abases = small + medium + large + vlarge + massive
bases = small
alg = ["boruta","pearson","spearman","kendall","random"]

db  = RepositorySQL("postgresql://postgres:HBynafIjIv1u6MgH@db.putqkagdjonralzjzvuw.supabase.co:5432/postgres")
#db:RepositorySQL = RepositorySQL("sqlite:///./networks.db")
if __name__ == "__main__":
    for base in abases:
        conversor(base,db)

    for base in bases:
        r = db.search("optimization", {"base": base})
        data = {x['algorithm']: dict(x) for x in r}
        if not 'random' in data.keys():
            random(base,db)
        if not 'boruta' in data.keys():
            boruta(base,db)
        if not 'pearson' in data.keys():
            pearson(base,db)
        if not 'spearman' in data.keys():
            spearman(base,db)
        if not 'kendall' in data.keys():
            kendall(base,db)

    for base in bases:
        r = db.search("optimization",{"base": base})
        if len(r)==6:
            data = {x['algorithm']: dict(x) for x in r}
            for a in alg:
                count_edges(base, a,data['art']['file'],data[a]['file'],db)
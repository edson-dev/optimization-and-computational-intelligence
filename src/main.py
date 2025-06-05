#from counter import count_edges
#from converter import execute as conversor
from k2random import execute as random
from k2boruta import execute as boruta
from k2pearson import execute as pearson
from k2spearman import execute as spearman
from k2kendall import execute as kendall
from sql import RepositorySQL

db  = RepositorySQL("postgresql://postgres:HBynafIjIv1u6MgH@db.putqkagdjonralzjzvuw.supabase.co:5432/postgres")
#  db:RepositorySQL = RepositorySQL("sqlite:///./networks.db")
overide = False

small = ["asia","cancer","earthquake","sachs","survey"]
medium = ["alarm","child","insurance","water","mildew","barley"]
large = ["hailfinder","hepar2","win95pts"]
vlarge = ["andes","link","munin1","pathfinder","pigs"] #"diabetes"
massive = ["munin"]
info_bases = massive + vlarge + large + medium + small

exec_bases = small+medium #info_bases
alg = ["boruta","pearson","spearman","kendall","random"]


if __name__ == "__main__":
    for base in info_bases:
        ...#conversor(base, db)

    for base in exec_bases:
        r = db.search("optimization", {"base": base})
        data = {x['algorithm']: dict(x) for x in r}
        if not 'random' in data.keys() or overide:
            random(base, db)
        if not 'boruta' in data.keys() or overide:
            boruta(base, db)
        if not 'pearson' in data.keys() or overide:
            pearson(base, db)
        if not 'spearman' in data.keys() or overide:
            spearman(base, db)
        if not 'kendall' in data.keys() or overide:
            kendall(base, db)

    for base in info_bases:
        r = db.search("optimization",{"base": base})
        data = {x['algorithm']: dict(x) for x in r}
        for a in alg:
            if a in data.keys():
                ...#count_edges(base, a, data['art']['file'], data[a]['file'], db)
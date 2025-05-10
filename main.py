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
bases = ["asia"]
alg = ["boruta","pearson","spearman","kendall","random"]

db  = RepositorySQL("postgresql://postgres:HBynafIjIv1u6MgH@db.putqkagdjonralzjzvuw.supabase.co:5432/postgres")
db:RepositorySQL = RepositorySQL("sqlite:///./networks.db")
if __name__ == "__main__":
    for base in bases:
        conversor(base,db)

    for base in bases:
        random(base,db)
        boruta(base,db)
        pearson(base,db)
        spearman(base,db)
        kendall(base,db)

    for base in bases:
        for a in alg:
            count_edges(base, a,db)
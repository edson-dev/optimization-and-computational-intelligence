from counter import count_edges
from converter import execute as conversor
from k2random import execute as random
from k2boruta import execute as boruta
from k2pearson import execute as pearson
from k2spearman import execute as spearman
from k2kendall import execute as kendall

small = ["asia","cancer","earthquake","sachs","survey"]
medium = ["alarm","barley","child","insurance","mildew","water"]
large = ["hailfinder","hepar2","win95pts"]
vlarge = ["andes","diabetes","link","munin1","pathfinder","pigs"]
massive = ["munin"]
bases = ["diabetes"]
alg = ["boruta","pearson","spearman","kendall","random"]

if __name__ == "__main__":
    for base in bases:
        conversor(base)
        #random(base)
        #boruta(base)
        #pearson(base)
        #spearman(base)
        #kendall(base)
    for base in bases:
        for a in alg:
            ...
            #count_edges(base, a)
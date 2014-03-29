#!/usr/bin/env python
'''kMeans

Usage:
    kmeans.py [--normalize] [--distance] [--k=<k>] [--base=<base>]
    kmeans.py (-h | --help)
    kmeans.py --version

Options:
    -h --help       Show the help
    --version       Show the version
    --normalize     Normalize the data
    --distance      Weight the values by the distance
    --k=<n>         the number of neighbors [default: 3]
    --base=<base>   the file base [default: mt_]

'''

from scipy.spatial.distance import cdist
from scipy.io.arff import loadarff
from pandas import DataFrame
from numpy import array
import numpy as np
import docopt

class KMeans:
    def __init__(self, data, k, random):
        self.data = data
        self.k = k
        self.random = random
        # init
        self.centroids = []
        if random:
            ixs = np.random.choice(data.index, k)
        else:
            ixs = data.index[:k]
        self.centroids = [data.loc[i] for i in ixs]

    def step(self):
        groups = [[] for c in self.centroids]
        for i in self.data.index:
            p = self.data.loc[i]
            best = None
            for i, c in enumerate(self.centroids):
                dst = distance(c, p)
                if best is None or dst < best[1]:
                    best = i, dst
            groups[best[0]].append(p)
        news = []
        change = 0
        for i, group in enumerate(groups):
            newc = avg_points(group)
            change += dst(self.centroids[i], newc)
            news.append(newc)
        self.centroids = map(avg_points, groups)

    def run(self):
        while True:

def run_kmeans(fname, k=4, random=False):
    data, meta = loadarff(fname)
    data = DataFrame(data)
    mines = KMeans(data, k, random=random)

# vim: et sw=4 sts=4

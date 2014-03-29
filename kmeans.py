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
import numpy
import docopt

class KMeans:
    def __init__(self, data, k, random):
        self.data = data
        self.k = k
        self.random = random
        # init
        self.centroids = []

def run_kmeans(fname, k=4, random=False):
    data, meta = loadarff(fname)
    data = DataFrame(data)
    mines = KMeans(data, k, random=random)

# vim: et sw=4 sts=4

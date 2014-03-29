#!/usr/bin/env python
'''HAC

Usage:
    hac.py [--normalize] [--distance] [--k=<k>] [--base=<base>]
    hac.py (-h | --help)
    hac.py --version

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
import math

from utils import *

def make_distances(data, types):
    zeros = np.zeros((len(data), len(data)))
    for i in xrange(len(data)):
        for j in xrange(i+1, len(data)):
            zeros[i,j] = zeros[j,i] = distance(data.iloc[i], data.iloc[j], types)
    return zeros

class HAC:
    def __init__(self, data, types, single=True):
        self.data = data
        self.types = types
        self.single = single
        self.clusters = [[a,] for a in range(len(data.index))]

        self.distances = make_distances(data, types)

    def dist(self, one, two):
        best = None
        for a in one:
            for b in two:
                d = distance(self.data.iloc[a], self.data.iloc[b], self.types)
                if best is None:
                    best = d
                elif (d < best if self.single else d > best):
                    best = d
        return best

    def step(self):
        mx = np.empty((len(self.clusters), len(self.clusters)))
        mx[:] = np.inf
        best = None
        for i in xrange(len(self.clusters)):
            for j in xrange(i+1, len(self.clusters)):
                d = self.dist(self.clusters[i], self.clusters[j])
                if best is None or d < best[0]:
                    best = d, i, j
        print 'merging', best[1], best[2], best[0]
        self.clusters[best[1]] += self.clusters.pop(best[2])

    def serr(self):
        serrs = []
        for ixs in self.clusters:
            points = [self.data.iloc[ix] for ix in ixs]
            centroid = avg_points(points, self.types)
            sse = 0
            for point in points:
                sse += distance(centroid, point, self.types)**2
            serrs.append(sse)
        return sum(serrs), serrs

    def run(self, k=5):
        while len(self.clusters) > 5:
            self.step()
        
        return self.serr()

def main():
    pass

def debug():
    data, meta = loadarff('./laborWithID.arff')
    data = DataFrame(data)
    data = data[data.columns[1:-1]]
    types = [meta[name] for name in meta.names()[1:-1]]
    hac = HAC(data, types)
    err = hac.run(5)
    print 'err', err
    for c in hac.clusters:
        print c

if __name__ == '__main__':
    debug()

# vim: et sw=4 sts=4

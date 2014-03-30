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

def read_dists(sz):
    dists = np.zeros((sz, sz))
    for i, lin in enumerate(open('./mx.txt').read().split('\n')):
        for j, n in enumerate(lin.split(';')):
            if not n:continue
            dists[i,j] = float(n)
    return dists

class HAC:
    def __init__(self, data, types, single=True):
        self.data = data
        self.types = types
        self.single = single
        self.clusters = [[a,] for a in range(len(data.index))]

        self.distances = make_distances(data, types)
        # self.distances = read_dists(len(data))
        # for line in self.distances:
            # print ';'.join(map(str, line))
        # fail

    def dist(self, one, two):
        return big_dist(one, two, self.single, self.distances)

    def step(self):
        # mx = np.empty((len(self.clusters), len(self.clusters)))
        # mx[:] = np.inf
        best = None
        for i in xrange(len(self.clusters)):
            for j in xrange(i+1, len(self.clusters)):
                d = self.dist(self.clusters[i], self.clusters[j])
                if best is None or d < best[0]:
                    best = d, i, j
        print len(self.clusters), 'merging', best[1], best[2], best[0]
        self.clusters[best[1]] += self.clusters.pop(best[2])

    def serr(self):
        serrs = []
        centroids = []
        instances = []
        for ixs in self.clusters:
            points = [self.data.iloc[ix] for ix in ixs]
            instances.append(points)
            centroid = avg_points(points, self.types)
            centroids.append(centroid)
            sse = 0
            for point in points:
                sse += distance(centroid, point, self.types)**2
            serrs.append(sse)
        return sum(serrs), serrs, centroids, davies(zip(instances, centroids), self.types)

    def run(self, k=5):
        while len(self.clusters) > k:
            self.step()
        
        # print 'Single?', self.single
        return self.serr()

def abalone(k, tok=None, single=True, norm=True):
    data, meta = loadarff('./abalone500.arff')
    data = DataFrame(data)
    if norm:
        normalize(data, meta)
    types = [meta[name] for name in meta.names()]
    hac = HAC(data, types, single)

    sse, _, _, dav= hac.run(k)
    print 'Atk,', k, sse, dav
    if tok:
        for i in range(k-1, tok-1, -1):
            sse, _, _, dav = hac.run(i)
            print i, ',', sse, ',', dav
    print 'Single', single

def iris(k, single=True, tok=None, outin=True):
    data, meta = loadarff('./iris.arff')
    data = DataFrame(data)
    if not outin:
        data = data[data.columns[:-1]]
    types = [meta[name] for name in meta.names()]
    if not outin:
        types = types[:-1]
    hac = HAC(data, types, single)

    sse, _, _ = hac.run(k)
    print 'Atk,', k, sse
    if tok:
        for i in range(k-1, tok-1, -1):
            sse, _, _ = hac.run(i)
            print i, ',', sse
    print 'Single', single
    if outin:
        print 'Output class included'
    # print 'err', sse
    # for err, centroid, cluster in zip(errs, centroids, hac.clusters):
        # print ','.join(map(str, centroid + [len(cluster), err]))

def n1():
    data, meta = loadarff('./sponge.arff')
    data = DataFrame(data)
    types = [meta[name] for name in meta.names()]
    hac = HAC(data, types, False)
    sse, errs, centroids = hac.run(4)
    print 'err', sse
    for err, centroid, cluster in zip(errs, centroids, hac.clusters):
        print ','.join(map(str, centroid + [len(cluster), err]))

def debug():
    data, meta = loadarff('./laborWithID.arff')
    data = DataFrame(data)
    data = data[data.columns[1:-1]]
    types = [meta[name] for name in meta.names()[1:-1]]
    hac = HAC(data, types, True)
    err = hac.run(5)
    print 'err', err
    for c in hac.clusters:
        print c

if __name__ == '__main__':
    abalone(7, 2, True, True)

# vim: et sw=4 sts=4

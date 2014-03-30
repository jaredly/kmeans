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
import math

from utils import *

class KMeans:
    def __init__(self, data, types, k, random, threshhold=0):
        self.data = data
        self.k = k
        self.random = random
        self.threshhold = threshhold
        self.types = types
        # init
        self.centroids = []
        if random:
            ixs = np.random.choice(data.index, k)
        else:
            ixs = data.index[:k]
        self.centroids = [data.loc[i] for i in ixs]
        self.isse = self.regroup()
        # print 'initial  erro', self.isse

    def davies(self):
        return davies(zip(self.groups, self.centroids), self.types)

    def regroup(self):
        groups = [[] for c in self.centroids]
        sse = 0
        sses = [0 for x in self.centroids]
        assignments = []
        for i in self.data.index:
            p = self.data.loc[i]
            best = closest(p, self.centroids, self.types)
            # print i, best
            groups[best[0]].append(p)
            assignments.append(best[0])
            sses[best[0]] += best[1]**2
            sse += best[1]**2
        self.groups = groups
        # for i in range(0, len(assignments), 10):
            # print ' '.join('{}={}'.format(j,assignments[j]) for j in range(i,i+10) if j < len(assignments))
        # print map(len, groups)
        return sse, sses

    def step(self):
        news = []
        change = 0
        for i, group in enumerate(self.groups):
            # print 'group', i, len(group)
            # for n in group:print list(n)
            newc = avg_points(group, self.types)
            news.append(newc)
            # print ', '.join(str(x) for x in newc)
        # print news
        self.centroids = news
        return self.regroup()

    def run(self):
        sses = [self.isse]
        for i in xrange(10000):
            sses.append(self.step())
            # print 'Errpr', sses[-1]
            if len(sses) > 4:
                sses = sses[-4:]
                if sses[-1][0] >= sses[0][0]:
                    break
        else:
            print 'Maxed out the iterations'
        return i, sses[0]

def debug():
    data, meta = loadarff('./laborWithID.arff')
    data = DataFrame(data)
    data = data[data.columns[1:-1]]
    types = [meta[name] for name in meta.names()[1:-1]]
    means = KMeans(data, types, 5, random=False)
    iters = means.run()
    print iters
    for c in means.centroids:
        print c

def n1():
    data, meta = loadarff('./sponge.arff')
    data = DataFrame(data)
    types = [meta[name] for name in meta.names()]
    means = KMeans(data, types, 4, False)
    i, (sse, errs) = means.run()

    print 'err', sse
    for err, centroid, cluster in zip(errs, means.centroids, means.groups):
        print ','.join(map(str, centroid + [len(cluster), err]))


def run_kmeans(fname, k, random=False):
    data, meta = loadarff('./laborWithID.arff')
    data = DataFrame(data)
    types = [meta[name] for name in meta.names()]
    means = KMeans(data, types, k, random=random)
    iters = means.run()
    print iters
    for c in means.centroids:
        print c

def kbest(data, types, k, num=10):
    best = kme(data, types, k)
    for i in range(num-1):
        a, b, d = kme(data, types, k)
        if d < best[2]:
            best = a, b, d
    return best

def kme(data, types, k):
    means = KMeans(data, types, k, True)
    a, b = means.run()
    for group in means.groups:
        if not len(group):
            # print 'null group'
            return kme(data, types, k)
    return a, b, means.davies()

def run_one(fname, k, tok=None, norm=True, skip_last=False):
    data, meta = loadarff(fname)
    data = DataFrame(data)
    if norm:
        normalize(data, meta)
    types = [meta[name] for name in meta.names()]

    if skip_last:
        data = data[data.columns[:-1]]
        types = types[:-1]

    _, (sse, _), dav = kbest(data, types, k)

    print 'Atk,', k, ',', sse, dav
    if tok:
        for i in range(tok, k):
            _, (sse, _), dav = kbest(data, types, i)
            print i, ',', sse, dav
    if skip_last:
        print 'Skipping last'
    if norm:
        print 'Normalized'

def abalone(k, tok=None, norm=False):
    data, meta = loadarff('./abalone500.arff')
    data = DataFrame(data)
    if norm:
        normalize(data, meta)
    types = [meta[name] for name in meta.names()]

    means = KMeans(data, types, k, True)
    _, (sse, _) = means.run()

    print 'Atk,', k, ',', sse, means.davies()
    if tok:
        for i in range(tok, k):
            means = KMeans(data, types, i, True)
            _, (sse, _) = means.run()
            print i, ',', sse, means.davies()

def iris(k, tok=None, outin=True):
    data, meta = loadarff('./iris.arff')
    data = DataFrame(data)
    if not outin:
        data = data[data.columns[:-1]]
    types = [meta[name] for name in meta.names()]
    if not outin:
        types = types[:-1]

    means = KMeans(data, types, k, True)
    _, (sse, _) = means.run()

    print 'Atk,', k, ',', sse
    if tok:
        for i in range(tok, k):
            means = KMeans(data, types, i, True)
            _, (sse, _) = means.run()
            print i, ',', sse
    if outin:
        pass#print 'Output class included'
    # print 'err', sse
    # for err, centroid, cluster in zip(errs, centroids, hac.clusters):
        # print ','.join(map(str, centroid + [len(cluster), err]))


if __name__=='__main__':
    # abalone(7, 2, norm=True)
    run_one('./abalone500.arff', 7, 2, skip_last=True)

# vim: et sw=4 sts=4

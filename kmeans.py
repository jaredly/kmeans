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
        print 'initial  erro', self.isse

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
        for i in range(0, len(assignments), 10):
            print ' '.join('{}={}'.format(j,assignments[j]) for j in range(i,i+10) if j < len(assignments))
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
            print ', '.join(str(x) for x in newc)
        # print news
        self.centroids = news
        return self.regroup()

    def run(self):
        sses = [self.isse]
        for i in xrange(10000):
            sses.append(self.step())
            print 'Errpr', sses[-1]
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


def run_kmeans(fname, k, random=False):
    data, meta = loadarff('./laborWithID.arff')
    data = DataFrame(data)
    types = [meta[name] for name in meta.names()]
    means = KMeans(data, types, k, random=random)
    iters = means.run()
    print iters
    for c in means.centroids:
        print c

if __name__=='__main__':
    debug()

# vim: et sw=4 sts=4

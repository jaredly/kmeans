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

def avg_ones(ones, t):
    if t == 'numeric':
        real = [x for x in ones if not np.isnan(x)]
        if not real:
            return np.nan
        return sum(real)/len(real)
    if t == 'nominal':
        counts = {}
        for i in ones:
            if not i in counts:counts[i] = 1
            else: counts[i] += 1
        items = sorted(counts.items(), (lambda x,y:y[1]-x[1]))
        if items[0][0] == '?' and len(items) > 1:
            return items[1][0]
        return items[0][0]
    raise Exception("Invalid type?" + t)

def avg_points(points, types):
    return [avg_ones(ones, t) for ones, t in zip(zip(*points), types)]

def distance(a, b, types):
    total = 0
    for m, n, t in zip(a,b,types):
        if t == 'numeric':
            if np.isnan(m) or np.isnan(n):
                total += 1
            else:
                total += (m-n)**2
        elif t == 'nominal':
            if '?' in (m, n) or m != n:
                total += 1
        else:
            raise Exception('unknown {} {} {}'.format(t, m, n))
    return math.sqrt(total)

def closest(inst, cents, types):
    best = None
    for ix, c in enumerate(cents):
        dst = distance(c, inst, types)
        # print dst
        if best is None or dst < best[1]:
            best = ix, dst
    return best

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
        assignments = []
        for i in self.data.index:
            p = self.data.loc[i]
            best = closest(p, self.centroids, self.types)
            # print i, best
            groups[best[0]].append(p)
            assignments.append(best[0])
            sse += best[1]**2
        self.groups = groups
        for i in range(0, len(assignments), 10):
            print ' '.join('{}={}'.format(j,assignments[j]) for j in range(i,i+10) if j < len(assignments))
        # print map(len, groups)
        return sse

    def step(self):
        news = []
        change = 0
        for i, group in enumerate(self.groups):
            print 'group', i, len(group)
            # for n in group:print list(n)
            newc = avg_points(group, self.types)
            news.append(newc)
            print newc
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
                if sses[-1] >= sses[0]:
                    break
        else:
            print 'Maxed out the iterations'
        return i

def run_kmeans(fname, k=5, random=False):
    data, meta = loadarff(fname)
    data = DataFrame(data)
    data = data[data.columns[1:-1]]
    types = [meta[name][0] for name in meta.names()[1:-1]]
    means = KMeans(data, types, k, random=random)
    iters = means.run()
    print iters
    for c in means.centroids:
        print c


if __name__=='__main__':
    run_kmeans('./laborWithID.arff')

# vim: et sw=4 sts=4

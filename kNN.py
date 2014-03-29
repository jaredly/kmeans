#!/usr/bin/env python
'''kNN Awesomez

Usage:
    kNN.py [--normalize] [--distance] [--k=<k>] [--base=<base>]
    kNN.py (-h | --help)
    kNN.py --version

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

DEBUG = False

class NearestNeighbor:
    def __init__(self, meta, data, target, k=3, distance=False):
        self.data = data
        self.meta = meta
        self.target = target
        self.distance = distance

    def calc(self, data):
        goods = list(self.data.columns)
        goods.remove(self.target)
        print 'valid'
        import time
        start = time.time()

        # dists is a len(data) x len(self.data) matrix
        dists = DataFrame(cdist(array(self.data[goods]), array(data[goods]), 'euclidean'))
        print time.time() - start
        print 'doneval'
        if DEBUG:print dists
        self.dists = dists

    def validate(self, data, ninstances):
        '''Returns accuracy?'''
        wrong = 0

        for i in data.index:
            dlist = self.dists[i].copy()
            dlist.sort()

            votes = {}
            if DEBUG:print dlist.index
            if DEBUG:print dlist
            for ix in range(0, ninstances):
                cls = self.data.loc[dlist.index[ix]][self.target]
                if DEBUG:print ix, dlist.index[ix], cls
                if not cls in votes:
                    votes[cls] = (1/dlist.loc[dlist.index[ix]]**2) if self.distance else 1
                else:
                    votes[cls] += (1/dlist.loc[dlist.index[ix]]**2) if self.distance else 1
            most = None
            for k, v in votes.iteritems():
                if most is None or v > most[1]:
                    most = k, v

            cls = most[0]
            if DEBUG:print votes

            # item = data.loc[i]
            # cls = self.classify(item)
            if data.loc[i][self.target] != cls:
                wrong += 1
                # print cls, data.loc[i][self.target]
            # print '.',
            # if i > 20:break
        print wrong, len(data)
        return wrong / float(len(data))

def norms(one, two, cols):
    for c in cols:
        mn = min([one[c].min(), two[c].min()])
        mx = max([one[c].max(), two[c].max()])
        one[c] -= mn
        one[c] /= mx - mn
        two[c] -= mn
        two[c] /= mx - mn

def main(k=3, normalize=False, distance=True, base='mt_', ks=[]):
    train, mtrain = loadarff(base + 'train.arff')
    train = DataFrame(train)
    test, mtest = loadarff(base + 'test.arff')
    test = DataFrame(test)

    cols = [col for col in mtrain.names() if mtrain[col][0] == 'numeric']

    if normalize:
        norms(test, train, cols)

    learner = NearestNeighbor(mtrain, train, mtrain.names()[-1], distance=distance)
    learner.calc(test)
    import time
    print 'testing', [k]
    start = time.time()
    err = learner.validate(test, k)
    print 'Err:', err, 'Acc:', 1-err
    print 'Time', time.time() - start
    if not ks: return err
    errs = {}
    errs[k] = err
    for ok in ks:
        print 'testing'
        start = time.time()
        err = learner.validate(test, ok)
        print 'Err:', err, 'Acc:', 1-err
        print 'Time', time.time() - start
        errs[ok] = err
    return errs

if __name__ == '__main__':
    args = docopt.docopt(__doc__, version='kNN 1.0')
    main(k=int(args['--k']), distance=args['--distance'], normalize=args['--normalize'], base=args['--base'])

# vim: et sw=4 sts=4

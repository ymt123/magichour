from collections import Counter
from itertools import permutations
import hashlib


# return a md5 string representation of input string
def makeHash(s):

    m = hashlib.md5()
    m.update(s)
    return m.hexdigest()


# calculate the magnitude of a partition
def getMagnitude(C):
    retval = 0
    for key, count in C.iteritems():
        retval = retval + int(count)
    return retval


# calculate the best partition for X to be in
# using the cheat sum(p(r,Cdest))
def argMaxPhiSimple(C, X, G):
    numGroups = len(C)

    # see which group X should be in to maximize
    currentGroup = G[makeHash(X)]

    retScore = 0.0
    retval = currentGroup

    # make the tuples
    Xr = Counter(list(permutations(X.rstrip().split(), 2)))

    for nextGroup in range(numGroups):

        # dont consider transition to same group
        if nextGroup == currentGroup:
            continue

        currentScore = 0.0
        for r in Xr:
            if r in C[nextGroup]:
                currentScore = currentScore + C[nextGroup].get(r)

        # TODO make sure this is the correct way to calculate
        currentScore = currentScore / getMagnitude(C[nextGroup])

    # keep tabs of who is winning
    if retScore < currentScore:
        retScore = currentScore
        retval = currentGroup

    return retval


# store the data histograms
# in each parition
def randomSeeds(D, k, G):

    C = [dict() for _ in range(k)]
    partition = 0
    for d in D:
        partition = (partition + 1) % k
        # make histograms of loglines
        # TODO make sure that is is correct way of
        # assigning groups to a message
        G[makeHash(d)] = partition
        Xr = Counter(list(permutations(d.strip().split(), 2)))

        for key, count in Xr.iteritems():
            if key not in C[partition]:
                C[partition][key] = 0
            C[partition][key] = C[partition][key] + int(count)

    return C


# move X from partition i to partition j
def changePartition(C, X, G, i, j):

    # TODO would a binary version of this be sufficient?

    G[makeHash(X)] = j

    Xr = Counter(list(permutations(X.rstrip().split(), 2)))

    for r, count in Xr:
        # remove from i
        C[i][r] = C[i][r] - count

        # add to j
        if r not in C[j]:
            C[j][r] = 0

        C[j][r] = C[j][r] + count


# comare two lists of dictionaries for equality
# dictionaries assumed to be the same length
def listDictEqual(C, CLast):
    for i, s in enumerate(C):
        if s != CLast[i]:
            return False
    return True


# D : log message set
# k : number of groups to partition
# returns: C: partitions
def logSig_localSearch(D, k):

    # Create a map G to store messages group index
    G = dict()

    CLast = [dict() for _ in range(k)]
    C = randomSeeds(D, k, G)

    # place each logline into a set
    # TODO see if this would be better to conserve memory
    # by making this a k way lookup

    # TODO lookup to see if this always returns the same way
    # for i, Ci in enumerate(C):
    #    for X in Ci:
    #        G[makeHash(X)] = i

    # TODO should this be an energy measure
    # instead of dict comp?
    while not listDictEqual(C, CLast):
        print 'looping'

        CLast = C

        for Xj in D:
            i = G[makeHash(Xj)]
            jStar = argMaxPhiSimple(C, Xj, G)
            print 'i = %i, jStar= %i' % (i, jStar)
            if i != jStar:
                print 'moving %s from %i to %i' % (Xj, i, jStar)
                changePartition(C, Xj, G, i, jStar)
            # endif
        # endfor
    # end while
    return C


def main():

    a = open('testFiles/logFile', 'r')
    D = a.readlines()
    out = logSig_localSearch(D, 3)
    for i in out:
        print ('output %s' % i)


if __name__ == "__main__":
    main()
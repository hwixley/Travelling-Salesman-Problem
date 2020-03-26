import math
from operator import itemgetter  # Solely for the implementation of my own algorithm


def euclid(p, q):
    x = p[0] - q[0]
    y = p[1] - q[1]
    return math.sqrt(x * x + y * y)


class Graph:

    # Complete as described in the specification, taking care of two cases:
    # the -1 case, where we read points in the Euclidean plane, and
    # the n>0 case, where we read a general graph in a different format.
    # self.perm, self.dists, self.n are the key variables to be set up.
    def __init__(self, n, filename):
        file = open(filename)  # + ".txt")
        numNodes = 0
        points = []
        self.dists = []

        if n == -1:
            for line in file:
                b = line.find(' ', 1, 2)
                if b == -1:
                    x = line[1:4]
                else:
                    x = line[2:4]

                c = line.find(' ', 6, 7)
                if c == -1:
                    y = line[6:]
                else:
                    y = line[7:]

                points.append([int(x), int(y)])
                numNodes += 1

            self.n = numNodes

            for i in range(0, numNodes):  # Filling self.dists 2D list with appropriate values
                row = []
                for j in range(0, numNodes):
                    row.append(euclid(points[i], points[j]))
                self.dists.append(row)
                row = []

        elif n > 0:
            nodes = []
            for line in file:
                points.append([int(line[0:1]), int(line[2:3]), int(line[4:5])])

                alreadyExplored = [False, False]
                for i in nodes:
                    if i == int(line[0:1]):
                        alreadyExplored[0] = True
                    if i == int(line[2:3]):
                        alreadyExplored[1] = True

                if alreadyExplored[0] == False:
                    numNodes += 1
                    nodes.append(int(line[0:1]))
                if alreadyExplored[1] == False:
                    numNodes += 1
                    nodes.append(int(line[2:3]))

            self.n = numNodes
            self.dists = [[0 for i in range(numNodes)] for j in range(numNodes)]

            for p in points:
                self.dists[p[0]][p[1]] = p[2]
                self.dists[p[1]][p[0]] = p[2]

        self.perm = [[0] * numNodes] * numNodes

        for k in range(0, numNodes):
            self.perm[k] = k

    # Complete as described in the spec, to calculate the cost of the
    # current tour (as represented by self.perm).
    def tourValue(self):
        cost = 0
        i = -1

        for j in self.perm:
            if i != -1:
                cost += self.dists[i][j]
            i = j
        cost += self.dists[self.perm[len(self.perm) - 1]][self.perm[0]]

        return cost

    # Attempt the swap of cities i and i+1 in self.perm and commit
    # commit to the swap if it improves the cost of the tour.
    # Return True/False depending on success.
    def trySwap(self, i):
        oldCost = self.tourValue()

        if i + 1 == len(self.perm):
            indexI2 = 0
        else:
            indexI2 = i + 1

        newI = self.perm[indexI2]
        newI2 = self.perm[i]
        self.perm[indexI2] = newI2
        self.perm[i] = newI

        newCost = self.tourValue()

        if newCost < oldCost:
            return True
        else:
            self.perm[i] = newI2
            self.perm[indexI2] = newI
        return False

    # Consider the effect of reversing the segment between
    # self.perm[i] and self.perm[j], and commit to the reversal
    # if it improves the tour value.
    # Return True/False depending on success.              
    def tryReverse(self, i, j):
        oldCost = self.tourValue()

        iIn = self.perm[i]
        iInP = self.perm[i - 1]
        jIn = self.perm[j]
        jInP = self.perm[j + 1]

        newCost = oldCost - self.dists[iInP][iIn] - self.dists[jIn][jInP] + self.dists[iInP][jIn] + self.dists[iIn][
            jInP]

        if newCost < oldCost:
            rev = [0 for i in range(j - i + 1)]
            for v in range(j - i + 1):
                rev[v] = (self.perm[i + v])

            for z in range(j - i + 1):
                self.perm[i + z] = rev[j - i - z]

            return True
        else:
            return False

    def swapHeuristic(self):
        better = True
        while better:
            better = False
            for i in range(self.n):
                if self.trySwap(i):
                    better = True

    def TwoOptHeuristic(self):
        better = True
        while better:
            better = False
            for j in range(self.n - 1):
                for i in range(j):
                    if self.tryReverse(i, j):
                        better = True

    # Implement the Greedy heuristic which builds a tour starting
    # from node 0, taking the closest (unused) node as 'next'
    # each time.
    def Greedy(self):
        avNodes = self.perm[1:]
        greedyOrder = [0]

        for i in range(1, self.n):
            origNode = greedyOrder[len(greedyOrder) - 1]
            minVal = 100000

            for p in avNodes:
                if self.dists[origNode][p] < minVal:
                    destNode = p
                    minVal = self.dists[origNode][destNode]

            greedyOrder.append(destNode)
            avNodes.remove(destNode)

        self.perm = greedyOrder

    # CUSTOM ALGORITHM 'TEMPERATE' ASSOCIATED HELPER FUNCTIONS
    def createDistAverage(self, n):     # Returns the average distance for a given node n.
        mean = 0.0
        sum = 0

        for i in range(self.n):
            if i != n:
                sum += self.dists[n][i]

        mean = sum / self.n

        return mean

    def createDistAverages(self):   # Returns list of tuples (av. dist. , node) ordered by av. dist. smallest to highest
        meanList = []

        for i in range(self.n):
            meanList.append([self.createDistAverage(i), i])

        return sorted(meanList, key=itemgetter(0))

    def findNodeTransitions(self, node):    # Returns ordered list of node transitions ordered from low to high
        trans = []
        for i in range(self.n):
            if i != node:
                trans.append([self.dists[node][i], i])  # A single node transition represented by: [dist. , dest. node]

        return sorted(trans, key=itemgetter(0))

    def bestAvailableNodeTrans(self, n, explored):  # Returns the best available node transition for n
        trans = self.findNodeTransitions(n)

        for t in trans:
            node = t[1]

            expBool = False
            for e in explored:  # Checks if the given node has been explored yet
                if node == e:
                    expBool = True

            if not expBool:
                return t    # If the given node is available, then this node's respective transition is returned

        return -1   # If no node transition is available for n, the function returns -1

    def createFragment(self, node, explored):   # Returns the best available fragment for a given node
        expandNode = self.bestAvailableNodeTrans(node, explored)

        if expandNode != -1:
            return [node, expandNode[1]]    # A single fragment represented by: [origin node , destination node]
        else:
            return []   # If there is no available fragment, function returns []

    def cleanFragments(self, fragments):
        explored = []
        clean = []

        for f in fragments:
            expBool = False
            for e in explored:
                if e == f:
                    expBool = True
                    break

            if not expBool:
                clean.append(f)
                explored.append([f[1], f[0]])

        return clean

    def createFragments(self):
        meanList = self.createDistAverages()
        fragments = []
        explored = []

        for i in range(self.n-1, -1, -1):
            node = meanList[i][1]

            frag = self.createFragment(node, explored)
            if frag:
                fragments.append(frag)

        return self.cleanFragments(fragments)

    # CUSTOM ALGORITHM 'TEMPERATE' APPROXIMATE OPTIMAL ROUTE FINDING FUNCTION
    def createRoute(self):
        frags = self.createFragments()
        route = [frags[0][0], frags[0][1]]
        fragments = frags[1:]
        explored = [frags[0][0], frags[0][1]]

        while len(route) != self.n-1:
            for f in fragments:
                endNode = route[len(route) - 1]

                if f[0] == endNode:
                    route.append(f[1])
                    explored.append(f[1])
                elif f[1] == endNode:
                    route.append(f[0])
                    explored.append(f[0])
                else:
                    print(route)
                    node = self.bestAvailableNodeTrans(endNode, explored)[1]
                    if node != -1:
                        route.append(node)
                        explored.append(node)
                    else:
                        print("no node transition found for " + str(endNode))

                    if len(route) == self.n - 1:
                        lastNode = -1
                        for a in range(self.n):
                            explBool = False
                            for r in route:
                                if r == a:
                                    explBool = True
                                    break
                            if not explBool:
                                lastNode = a
                                break
                        route.append(lastNode)

                        self.perm = route
                        return route













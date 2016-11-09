#!/usr/bin/python

from __future__ import division
from collections import defaultdict
from itertools import izip
import time
import sys

class Edge:
    def __init__ (self, origin=None):
        self.origin = origin
        self.weight = 1

    def __repr__(self):
        return "edge: {0} {1}".format(self.origin, self.weight)

class Airport:
    def __init__ (self, iden=None, name=None):
        self.code = iden
        self.name = name
        self.routes = set() # set of airports that have this as destination
        self.routeHash = defaultdict(int) # routeHash[origin] = weight
        self.outdegree = 0
        self.pageRank= 0

    def __repr__(self):
        return "{0:4s}\t{1:.8f}\t{2}".format(self.code, self.pageRank, self.name)

edgeList = [] # list of Edge
edgeHash = defaultdict(int) # edgeHash[(origin, destination)] = weight
airportList = [] # list of Airport
airportHash = dict() # airportHash[code] = Airport

EPSILON = 0.00001
MAX_ITERATIONS = 100
DAMPING_FACTOR = 0.85
AIRPORTS_FILE = "airports.txt"
ROUTES_FILE = "routes.txt"

def initialMessage():
    print "##############################################################################"
    print "                            PAGE RANK ALGORITHM                               "
    print "##############################################################################"
    print ""
    print "This program computes the Page Rank of a network of airports and flights"
    print "Page Rank algorithm uses the following parameters:"
    print "\t - MAX_ITERATIONS = {0}".format(MAX_ITERATIONS)
    print "\t - DAMPING_FACTOR = {0}".format(DAMPING_FACTOR)
    print "\t - EPSILON = {0}".format(EPSILON)
    print ""
    print "##############################################################################"
    print ""

def readAirports(fd):
    print "Reading Airport file from {0}".format(fd)

    airportsTxt = open(fd, "r")
    valid = invalid = 0
    for line in airportsTxt.readlines():
        airport = Airport()
        line = line.split(',')

        # Remove quotes
        name    = line[1][1:-1]
        country = line[3][1:-1]
        code    = line[4][1:-1]

        # Discard airports with invalid IATA codes
        if len(code) != 3:
            invalid += 1
            continue

        airport.name = name + ", " + country
        airport.code = code
        airportList.append(airport)
        airportHash[airport.code] = airport

        valid += 1

    airportsTxt.close()
    print "There were {0} airports with a valid IATA code".format(valid)
    print "There were {0} airports with an invalid IATA code\n".format(invalid)


def readRoutes(fd):
    print "Reading Routes file from {0}".format(fd)

    routesTxt = open(fd, "r")
    valid = invalid = 0
    for line in routesTxt.readlines():
        line = line.split(',')
        origin = line[2]
        destination = line[4]

        # Discard invalid IATA codes
        if len(origin) != 3 or len(destination) != 3:
            invalid += 1
            continue
        if origin not in airportHash or destination not in airportHash:
            invalid += 1
            continue

        e = Edge(origin)
        edgeList.append(e)
        edgeHash[(origin, destination)] += 1

        originAirport = airportHash[origin]
        destinationAirport = airportHash[destination]

        # Origin updates
        originAirport.outdegree += 1

        # Destination updates
        destinationAirport.routes.add(origin)
        destinationAirport.routeHash[origin] += 1

        valid += 1

    routesTxt.close()
    print "There were {0} valid routes".format(valid)
    print "There were {0} invalid routes".format(invalid)


def stopConditionIsReached(iterations, previousPageRank):
    if iterations >= MAX_ITERATIONS:
        return True

    currentPageRank = [airport.pageRank for airport in airportList]
    for current, previous in izip(currentPageRank, previousPageRank):
        if abs(current - previous) > EPSILON:
            return False

    return True


def computePageRank(airportPosition):
    destinationAirport = airportList[airportPosition]

    if destinationAirport.outdegree == 0:
        return 1.0/len(airportList)

    pageRank = 0
    for origin in destinationAirport.routes:
        originAirport = airportHash[origin]
        edgeWeight = destinationAirport.routeHash[origin]
        pageRank += originAirport.pageRank * edgeWeight/originAirport.outdegree

    return pageRank


def initializePageRanks(n):
    for airport in airportList:
        airport.pageRank = 1/n


def updatePageRanks(Q, previousPageRank):
    for i, airport in enumerate(airportList):
        previousPageRank[i] = airport.pageRank
        airport.pageRank = Q[i]


def computePageRanks():
    n = len(airportList)
    initializePageRanks(n)

    previousPageRank = [0] * n
    iterations = 0
    while not stopConditionIsReached(iterations, previousPageRank):

        Q = [0] * n
        for i in range(0, n):
            Q[i] = DAMPING_FACTOR*computePageRank(i) + (1-DAMPING_FACTOR)/n
            airport = airportList[i]
 
        updatePageRanks(Q, previousPageRank)
        iterations += 1

    return iterations


def outputPageRanks():
    print ""
    print "##############################################################################"
    print "\nResults:"
    print "Rank\tIATA\tPageRank\tName"

    ranking = sorted(airportList, key = lambda a: a.pageRank, reverse = True)
    for rank, airport in enumerate(ranking):
        print '{:4d}'.format(rank+1) + '\t' + str(airport)

def executionInfo(iterations, time):
    print ""
    print "##############################################################################"
    print "\nExecution information:"
    print "\t - #Iterations:", iterations
    print "\t - Time of computePageRanks():", time
    print ""

def main():
    initialMessage()
    readAirports(AIRPORTS_FILE)
    readRoutes(ROUTES_FILE)
    time1 = time.time()
    iterations = computePageRanks()
    time2 = time.time()
    outputPageRanks()
    executionInfo(iterations, time2-time1)


if __name__ == "__main__":
    sys.exit(main())

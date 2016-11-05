#!/usr/bin/python

from __future__ import division
from collections import namedtuple, defaultdict
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
        self.routes = [] # list of airports that have this as destination
        self.routeHash = defaultdict(int) # routeHash[origin] = weight
        self.outweight = 0
        self.pageRank= 0

    def __repr__(self):
        return "{0}\t{1}\t{2}".format(self.code, self.pageRank, self.name)

edgeList = [] # list of Edge
edgeHash = defaultdict(int) # edgeHash[(origin, destination)] = weight
airportList = [] # list of Airport
airportHash = dict() # airportHash[code] = Airport

EPSILON = 0.00001
MAX_ITERATIONS = 100
DAMPING_FACTOR = 0.8

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
        originAirport.outweight += 1

        # Destination updates
        destinationAirport.routes.append(origin)
        destinationAirport.routeHash[origin] += 1

        valid += 1

    routesTxt.close()
    print "There were {0} valid routes".format(valid)
    print "There were {0} invalid routes\n".format(invalid)
        

def stopConditionIsReached(iterations, previous):
    if iterations >= MAX_ITERATIONS:
        return True

    for airport, previous in izip(airportList, previous):
        current = airport.pageRank
        if abs(current - previous) > EPSILON:
            return False
    
    return True


def computePageRank(airportPosition):
    destinationAirport = airportList[airportPosition]
    
    pageRank = 0
    for origin in destinationAirport.routes:
        originAirport = airportHash[origin]
        pageRank += originAirport.pageRank * destinationAirport.routeHash[origin]/originAirport.outweight

    return pageRank

def initializePageRanks():
    n = len(airportList)
    for airport in airportList:
        airport.pageRank = 1/n


def updatePageRanks(Q, previous):
    for i, airport in enumerate(airportList):
        previous[i] = airport.pageRank
        airport.pageRank = Q[i]


def computePageRanks():
    initializePageRanks()
    n = len(airportList)
    previous = [0] * n
    iterations = 0
    while not stopConditionIsReached(iterations, previous):
        Q = [0] * n

        for i in range(0, n):
            Q[i] = DAMPING_FACTOR*computePageRank(i) + (1-DAMPING_FACTOR)/n

        updatePageRanks(Q, previous)
        iterations += 1

    return iterations


def outputPageRanks():
    print "IATA\tPageRank\tName"
    for airport in airportList:
        print airport


def main():
    readAirports("airports.txt")
    readRoutes("routes.txt")
    time1 = time.time()
    iterations = computePageRanks()
    time2 = time.time()
    outputPageRanks()

    print "#Iterations:", iterations
    print "Time of computePageRanks():", time2-time1


if __name__ == "__main__":
    sys.exit(main())
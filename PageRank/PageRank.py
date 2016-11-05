#!/usr/bin/python

from __future__ import division
from collections import namedtuple, defaultdict
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
        self.pageIndex = 0

    def __repr__(self):
        return "{0}\t{1}\t{2}".format(self.code, self.pageIndex, self.name)

edgeList = [] # list of Edge
edgeHash = defaultdict(int) # edgeHash[(origin, destination)] = weight
airportList = [] # list of Airport
airportHash = dict() # airportHash[code] = Airport

EPSILON = 0.001
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
        

def stopConditionIsReached(iterations, current, previous, epsilon):
    if iterations == 0 or iterations >= MAX_ITERATIONS:
        return True

    for i in range(len(current)):
        if abs(current[i] - previous[i]) > EPSILON:
            return False
    
    return True


def computePageRank(airportPosition, P):
    destinationAirport = airportList[airportPosition]
    
    pageRank = 0
    for j, origin in enumerate(a.routes):
        originAirport = airportHash[origin]
        pageRank += P[j] * destinationAirport.routeHash[origin]/originAirport.outweight

    return pageRank


def computePageRanks():
    n = len(airportList)
    P = [1/n] * n
    Q = [0] * n
    previous = current = Q
    iterations = 0
    while not stopConditionIsReached(iterations, current, previous):
        Q = [0] * n
        for i in range(0, n):
            Q[i] = DAMPING_FACTOR * computePageRank(i, P) + (1-L)/n
        previous = current
        current = Q
        iterations += 1
    for i, value in enumerate(current):
        airportList[i].pageIndex = value
    return curr

def outputPageRanks():
    for airport in airportList:
        print airport

def main():
    readAirports("airports.txt")
    readRoutes("routes.txt")
    time1 = time.time()
    #iterations = computePageRanks()
    time2 = time.time()
    #outputPageRanks()

    print "#Iterations:", iterations
    print "Time of computePageRanks():", time2-time1


if __name__ == "__main__":
    sys.exit(main())
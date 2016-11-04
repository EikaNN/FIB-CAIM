#!/usr/bin/python

from collections import namedtuple, defaultdict
import time
import sys

class Edge:
    def __init__ (self, origin=None):
        self.origin = origin # write appropriate value
        self.weight = 1      # write appropriate value

    def __repr__(self):
        return "edge: {0} {1}".format(self.origin, self.weight)
        
    ## write rest of code that you need for this class

class Airport:
    def __init__ (self, iden=None, name=None):
        self.code = iden
        self.name = name
        self.routes = []  # list of airports that have this as origin
        self.routeHash = defaultdict(int) # routeHash[origin] = weight
        self.outweight = 0 # write appropriate value

    def __repr__(self):
        return "{0}\t{2}\t{1}".format(self.code, self.name, self.pageIndex)

edgeList = [] # list of Edge
edgeHash = defaultdict(int) # hash of edge to ease the match: edgeHash[(origin, destination)] = weight
airportList = [] # list of Airport
airportHash = dict() # hash key IATA code -> Airport: airportHash[code] = AirportObject

def readAirports(fd):
    print "Reading Airport file from {0}".format(fd)
    airportsTxt = open(fd, "r")
    cont = 0
    for line in airportsTxt.readlines():
        a = Airport()
        try:
            temp = line.split(',')
            if len(temp[4]) != 5 :
                raise Exception('not an IATA code')
            a.name=temp[1][1:-1] + ", " + temp[3][1:-1]
            a.code=temp[4][1:-1]
        except Exception as inst:
            pass
        else:
            cont += 1
            airportList.append(a)
            airportHash[a.code] = a
    airportsTxt.close()
    print "There were {0} Airports with IATA code".format(cont)


def readRoutes(fd):
    print "Reading Routes file from {0}".format(fd)
    # write your code
    routesTxt = open(fd, "r")
    cont = 0
    for line in routesTxt.readlines():
        line = line.split(',')
        origin = line[2]
        destination = line[4]

        if len(origin) != 3 or len(destination) != 3:
            continue
        if origin not in airportHash or destination not in airportHash:
            continue

        e = Edge(origin)
        
        edgeList.append(e)

        originAirport = airportHash[origin]
        destinationAirport = airportHash[destination]

        # Origin
        #if destination not in originAirport.routes:
            #originAirport.routes.append(destination)
        originAirport.outweight += 1

        # Destination
        destinationAirport.routes.append(origin)
        destinationAirport.routeHash[origin] += 1
        
        '''
        if origin not in destinationAirport.routeHash:
            destinationAirport.routeHash[origin] += 1
        else:
            destinationAirport.routeHash[origin].weight += 1
        '''
        edgeHash[(origin, destination)] += 1

    routesTxt.close()
    print "There were {0} valid routes".format(cont)
        
def stopCond(curr,old,e):
  for i in range(len(curr)):
    if abs(curr[i] - old[i]) > e:
        print(curr[i], old[i])
        return False
  return True


def valuee(i,P):
  a = airportList[i]
  sum = 0
  for j, origin in enumerate(a.routes):
    originAirport = airportHash[origin]
    sum += P[j]*a.routeHash[origin]/originAirport.outweight
  return sum


def computePageRanks():
  n = len(airportList)
  P = [1.0/n] * n
  L = 0.8
  Q = [0] * n
  old = curr = Q
  iterations = 0
  while iterations == 0 or stopCond(curr,old, 1000):
    Q = [0]  * n
    for i in range(0, n):
      Q[i] = L * valuee(i,P) + (1.0 - L)/n
    old = curr
    curr = Q
    iterations += 1
  print("iterations: ", iterations)
  for i, value in enumerate(curr):
    airportList[i].pageIndex = value
  return curr

def outputPageRanks():
  pr = computePageRanks()
  for rank in pr:
    print rank
    # write your code
    pass

def main(argv=None):
    readAirports("airports.txt")
    readRoutes("routes.txt")
    time1 = time.time()
    iterations = computePageRanks()
    time2 = time.time()
    outputPageRanks()

    #for a in airportList:
        #print a

    print "#Iterations:", iterations
    print "Time of computePageRanks():", time2-time1


if __name__ == "__main__":
    sys.exit(main())
from pymongo import MongoClient
from csv import reader
from bson.code import Code
from collections import defaultdict
from time import time

GROCERIES_FILE = "groceries.csv"
DB = None

def initialMessage():
    print("##############################################################################")
    print("                         MARKET BASKET ANALYSIS                               ")
    print("##############################################################################")
    print()
    print("This program analyses a database of customer's purchases")
    print("MongoDB is used to compute a simple association rule miner")
    print()
    print("##############################################################################")
    print()

def readGroceries(fd):
    global DB
    conn = MongoClient()
    DB = conn.test
    DB.groceries.drop()

    print("Reading groceries file from {0}".format(fd))
    with open(fd, newline='') as csvfile:
        groceries = reader(csvfile, delimiter=',')
        for line in groceries:
            line = list(map(lambda l : l.strip(), line))
            d = {}
            d['content'] = line
            DB.groceries.insert(d)
    print("There were {0} transactions\n".format(DB.groceries.count()))

def processTransactions():
    singleItemsCount()
    pairItemsCount()

def singleItemsCount():
    mapper = Code("""
    function() {
        for (var i = 0; i < this.content.length; i++) {
            emit(this.content[i], 1);
        }
    }
                  """)

    reducer = Code("""
    function(key, values) {
        var total = 0;
        for (var i = 0; i < values.length; i++) {
            total += values[i];
        }
        return total;
    }
                   """)

    print("Computing single item transactions")
    start = time()

    DB.single.drop()
    DB.groceries.map_reduce(mapper, reducer, "single")

    end = time()
    print("We found {0} different single items".format(DB.single.count()))
    print("End of computation: {0:.3f} seconds\n".format(end-start))


def pairItemsCount():
    
    mapper = Code("""
    function() {
        for (var i = 0; i < this.content.length; i++) {
            for (var j = i+1; j < this.content.length; ++j) {
                if (this.content[i] < this.content[j]) {
                    emit({first: this.content[i], second: this.content[j]}, 1);
                }
                else {
                    emit({first: this.content[j], second: this.content[i]}, 1);
                }
            }            
        }
    }
                  """)
    
    reducer = Code("""
    function(key, values) {
        var total = 0;
        for (var i = 0; i < values.length; i++) {
            total += values[i];
        }
        return total;
    }
                   """)

    print("Computing pair item transactions")
    start = time()

    DB.pair.drop()
    DB.groceries.map_reduce(mapper, reducer, "pair")

    end = time()
    print("We found {0} different pairs of items".format(DB.pair.count()))
    print("End of computation: {0:.3f} seconds\n".format(end-start))


def findAssociationRules():
    pairs = [(0.01,0.01),(0.01,0.25),(0.01,0.5),(0.01,0.75),
             (0.05,0.25),(0.07,0.25),(0.2,0.25),(0.5,0.25)]
    associations = defaultdict(int)
    total_items = DB.groceries.count()
    rules = {4:[], 5:[], 6:[]}

    d = defaultdict(int)

    print("Computing association rules")
    print("Checking over {0} pairs of items".format(DB.pair.count()))
    start = time()

    for doc in DB.pair.find():
        item1 = doc['_id']['first']
        item2 = doc['_id']['second']
        counts_ab = doc['value']
        counts_a = DB.single.find({'_id':item1}).next()['value']
        counts_b = DB.single.find({'_id':item2}).next()['value']

        support = counts_ab / total_items
        confidence_a = counts_ab / counts_a
        confidence_b = counts_ab / counts_b

        for i, (support_threshold, confidence_threshold) in enumerate(pairs, start=1):

            if support > support_threshold and confidence_a > confidence_threshold:
                associations[(support_threshold, confidence_threshold)] += 1
                if i in [4, 5, 6]:
                    rules[i].append( (item1 ,item2) )

            if support > support_threshold and confidence_b > confidence_threshold:
                associations[(support_threshold, confidence_threshold)] += 1
                if i in [4, 5, 6]:
                    rules[i].append( (item2 ,item1) )

    end = time()
    print("End of computation {0:.3f} seconds".format(end-start))
    print()
    print("##############################################################################")
    print()
    print("Final Results:")
    print()    

    for i, (support_threshold, confidence_threshold) in enumerate(pairs, start=1):
        total_association = associations[ (support_threshold, confidence_threshold) ]
        print("Row {0}: With support {1:.2f} and confidence {2:.2f} we find {3:3d} associations rules".
              format(i, support_threshold, confidence_threshold, total_association))
       
    print()
    print("Association Rules:")
    for row, rules in rules.items():
        print("\nRow {0} rules:".format(row))
        if len(rules) == 0:
            print("\tThere are no rules for this row")
        for item1, item2 in rules:
            print("\t{0} -> {1}".format(item1, item2))

    print()
    print("##############################################################################")
    print()

def main():
    initialMessage()
    readGroceries(GROCERIES_FILE)
    processTransactions()
    findAssociationRules()

if __name__ == "__main__":
    main()

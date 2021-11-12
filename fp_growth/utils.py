from collections import defaultdict
from itertools import chain, combinations


#Fp tree node class
class Node:
    def __init__(self, Node_name,counter):
        self.name = Node_name
        self.count = counter
        self.nodeLink = None
        self.children = {}

def remove_sep(number):
	sep = ['-1','-2']

	if number in sep:
		return False
	else:
		return True

def loadingData(fname):
    itemSetList = []    
    with open(fname, 'r') as file:
        records = file.readlines()
        for line in records:
            line = list( filter(remove_sep, line.split()))
            itemSetList.append(line)
    return itemSetList

def generateInitalSet(dataset):
    frozen_Dictionaries = {}
    for trans in dataset:
      if frozenset(trans) in frozen_Dictionaries:
        frozen_Dictionaries[frozenset(trans)]=frozen_Dictionaries[frozenset(trans)]+1
      else:
        frozen_Dictionaries[frozenset(trans)] = 1
    return frozen_Dictionaries

def mergingStrategy(conditionalDatabase,Fptree,prevpath):
  for item,subtree in Fptree.children.items():
    current_count=subtree.count
    if item in conditionalDatabase:
      if(len(prevpath)>0):
        k=prevpath.split(",")
        if len(k[0])==0 :
          conditionalDatabase[item][frozenset(k[1:])]=current_count
        else:
          conditionalDatabase[item][frozenset(k)]=current_count
    else:
      conditionalDatabase[item]={}
      if(len(prevpath)>0):
        k=prevpath.split(",")
        if len(k[0])==0 :
          conditionalDatabase[item][frozenset(k[1:])]=current_count
        else:
          conditionalDatabase[item][frozenset(k)]=current_count
    path=prevpath+","+item
    mergingStrategy(conditionalDatabase,subtree,path)

def printfp(Fptree,prevpath):
  for item,subtree in Fptree.children.items():
    path=prevpath+item
    current_count=subtree.count
    print("item",item)
    print(prevpath,current_count)
    printfp(subtree,path)

def generateHeaderTable(dataset, minSupport):
    headerTable = {}
    for transaction in dataset:
        for item in transaction:
            headerTable[item] = dataset[transaction] + headerTable.get(item,0)
    itemsTobeDeleted = []
    for item, support in headerTable.items():
        if support < minSupport:
            itemsTobeDeleted.append(item)
    for item in itemsTobeDeleted:
        headerTable.pop(item)
    return headerTable


def createFPTree(dataset, minSupport, iterator):
    headerTable = generateHeaderTable(dataset, minSupport)
    iterator=iterator+1

    frequent_itemset = set(headerTable.keys())

    if len(frequent_itemset) == 0:
        return None, None

    root = Node('Null Set',1)

    for k in headerTable:
        headerTable[k] = [headerTable[k], None]

    for itemset,count in dataset.items():
        frequent_transaction = {}

        for item in itemset:
            if item in frequent_itemset:
                frequent_transaction[item] = headerTable[item][0]
        AddToTransaction = len(frequent_transaction) >= 1
        if AddToTransaction:
            ordered_itemset = [v[0] for v in sorted(frequent_transaction.items(), key=lambda p: p[1], reverse=True)]
            iterator=0
            addTransactionToTree(ordered_itemset, root, headerTable, count , iterator)

    return root, headerTable


def addNodeLink(startNode,targetNode,iterator):
    iterator =iterator+1
    while (startNode.nodeLink != None):
        startNode = startNode.nodeLink
    startNode.nodeLink = targetNode

def addTransactionToTree(itemset, FPTree, headerTable, count ,iterator):
    if itemset[0] in FPTree.children:
        FPTree.children[itemset[0]].count=FPTree.children[itemset[0]].count+count
    else:
        FPTree.children[itemset[0]] = Node(itemset[0], count)

        if headerTable[itemset[0]][1] == None:
            headerTable[itemset[0]][1] = FPTree.children[itemset[0]]
        else:
           iterator = 0
           addNodeLink(headerTable[itemset[0]][1], FPTree.children[itemset[0]],iterator)

    if len(itemset) >= 2:
        addTransactionToTree(itemset[1::], FPTree.children[itemset[0]], headerTable, count ,iterator)

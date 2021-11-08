from collections import defaultdict
from itertools import chain, combinations


class Node:
    def __init__(self, itemName, frequency, parentNode):
        self.itemName = itemName
        self.count = frequency
        self.parent = parentNode
        self.children = {}
        self.next = None

    def increment(self, frequency):
        self.count += frequency

    def display(self, ind=1):
        print('  ' * ind, self.itemName, ' ', self.count)
        for child in list(self.children.values()):
            child.display(ind+1)

def remove_sep(number):
	sep = ['-1','-2']

	if number in sep:
		return False
	else:
		return True

def getFromFile(fname):
    itemSetList = []
    frequency = []
    
    with open(fname, 'r') as file:
        records = file.readlines()
        for line in records:
            line = list(filter(remove_sep, line.split()))
            itemSetList.append(line)
            frequency.append(1)

    return itemSetList, frequency

def createHeaderTable(itemSetList, frequency):
    headerTable = defaultdict(int)
    # Counting frequency and create header table
    for idx, itemSet in enumerate(itemSetList):
        for itemIdx in range(len(itemSet)):
            headerTable[itemSet[itemIdx]] += frequency[idx]
    return headerTable

def insertToTree(fpTree, itemSetList, headerTable, frequency):
	# Update FP tree for each cleaned and sorted itemSet
    for idx, itemSet in enumerate(itemSetList):
        itemSet = [item for item in itemSet if item in headerTable]
        itemSet.sort(key=lambda item: headerTable[item][0], reverse=True)
        # Traverse from root to leaf, update tree with given item
        currentNode = fpTree
        for item in itemSet:
            currentNode = updateTree(item, currentNode, headerTable, frequency[idx])

def constructTree(itemSetList, frequency, minSup):
     
    # Counting frequency and create header table
    headerTable = createHeaderTable(itemSetList, frequency)
    # print(headerTable)
    # Deleting items below minSup
    headerTable = dict((item, sup) for item, sup in headerTable.items() if sup >= minSup)
    if(len(headerTable) == 0):
        return None, None

    # HeaderTable column [Item: [frequency, headNode]]
    for item in headerTable:
        headerTable[item] = [headerTable[item], None]
    # Init Null head node
    fpTree = Node('Null', 1, None)
    #Insert to Tree 
    insertToTree(fpTree, itemSetList, headerTable, frequency)
    return fpTree, headerTable

def updateTree(item, treeNode, headerTable, frequency):
    if item in treeNode.children:
        # If the item already exists, increment the count
        treeNode.children[item].increment(frequency)
    else:
        # Create a new branch
        newItemNode = Node(item, frequency, treeNode)
        treeNode.children[item] = newItemNode
        # Link the new branch to header table
        updateHeaderTable(item, newItemNode, headerTable)

    return treeNode.children[item]

def updateHeaderTable(item, targetNode, headerTable):
    if(headerTable[item][1] == None):
        headerTable[item][1] = targetNode
    else:
        currentNode = headerTable[item][1]
        # Traverse to the last node then link it to the target
        while currentNode.next != None:
            currentNode = currentNode.next
        currentNode.next = targetNode

if __name__ == '__main__':
	print(getFromFile("../BMS1_spmf.txt"))
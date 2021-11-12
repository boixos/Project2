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

def treeMining(FPTree, headerTable, minSupport, prefix, frequent_itemset,closed_maximum,support_count_subset):

    support_count=[v[1][0] for v in sorted(headerTable.items(),key=lambda p: p[1][0])]
    bigL = [v[0] for v in sorted(headerTable.items(),key=lambda p: p[1][0])]

    conditionalDatabase={}
    mergingStrategy(conditionalDatabase,FPTree,"")
    all_support_counts=[]
    lengthOfBigL = len(bigL)
    for i in range(lengthOfBigL):
        
        new_frequentset = prefix.copy()
        new_frequentset.append(bigL[i])

        recursive_purpose_new_frequentset=prefix.copy()
        recursive_purpose_new_frequentset.append(bigL[i])
        
        #add frequent itemset to final list of frequent itemsets
        frequent_itemset[tuple(new_frequentset)]=support_count[i]

        

        if bigL[i] in conditionalDatabase:
          Conditional_pattern_bases=conditionalDatabase[bigL[i]]
        else:
          Conditional_pattern_bases={}

        
        all_support_counts.append(support_count[i])

        iterator=0

        Conditional_FPTree, Conditional_header = createFPTree(Conditional_pattern_bases,minSupport,iterator)

        if Conditional_header ==None:
          closed_maximum[tuple(new_frequentset)]=support_count[i]

        if Conditional_header != None:
            treeMining(Conditional_FPTree, Conditional_header, minSupport, recursive_purpose_new_frequentset, frequent_itemset,closed_maximum,support_count[i])
    
    
    max_support_count=0
    lengthOfMaxSupportCount = len(all_support_counts) 
    for j in range(lengthOfMaxSupportCount):
      if max_support_count< all_support_counts[j] :
        max_support_count=all_support_counts[j]

    superset_found=False

    for super_items,super_support in closed_maximum.items():
      if set(tuple(prefix)).issubset(super_items) and super_support==support_count_subset:
        superset_found=True

    if superset_found==False and support_count_subset>max_support_count  :
      closed_maximum[tuple(prefix)]=support_count_subset


def fpgrowthFromFile(fname, minSup, minConf):
    itemSetList = loadingData(fname)
    # print(frequency)
    initSet = generateInitalSet(itemSetList)
    iterator=0
    # print(initSet)
    FPtree, headerTable = createFPTree(initSet, minSup,iterator)
    # print(headerTable)
    frequent_itemset = {}
    closed_maximum={}
    treeMining(FPtree, headerTable, minSup, [], frequent_itemset,closed_maximum,0)
    return frequent_itemset, closed_maximum

if __name__ == '__main__':
    freqItems, closedFreqItems = fpgrowthFromFile("../../test_data_2.txt", 2, 0.5)
    print(closedFreqItems)
    print(len(freqItems))
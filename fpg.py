import time
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
    dataset = []
    file = open(fname, 'r')    
    records = file.readlines()
    for line in records:
        line = list( filter(remove_sep, line.split()))
        dataset.append(line)
    frozen_Dictionaries = {}
    for i in range(len(dataset)):
      trans = dataset[i]  
      if frozenset(trans) in frozen_Dictionaries:
        frozen_Dictionaries[frozenset(trans)]=frozen_Dictionaries[frozenset(trans)]+1
      else:
        frozen_Dictionaries[frozenset(trans)] = 1
    return frozen_Dictionaries

def mergingStrategy(conditionalDatabase,Fptree,prevpath):
  for item in Fptree.children:
    subtree = Fptree.children[item]
    
    if item in conditionalDatabase:
      if(len(prevpath)>0):
        k=prevpath.split(",")
        lengthOfK = len(k[0])
        if lengthOfK == 0 :
          current_count=subtree.count
          conditionalDatabase[item][frozenset(k[1:])]=current_count
        else:
          current_count=subtree.count
          conditionalDatabase[item][frozenset(k)]=current_count
    else:
      conditionalDatabase[item]={}
      if(len(prevpath)>0):
        k=prevpath.split(",")
        lengthOfK = len(k[0])
        if lengthOfK == 0 :
          current_count=subtree.count
          conditionalDatabase[item][frozenset(k[1:])]=current_count
        else:
          current_count=subtree.count
          conditionalDatabase[item][frozenset(k)]=current_count
    path=prevpath + ","
    path = path + item
    mergingStrategy(conditionalDatabase,subtree,path)

def generateHeaderTable(headerTable, dataset, minSupport):
    
    for transaction in dataset:
        for item in transaction:
            headerTable[item] = dataset[transaction] + headerTable.get(item,0)
    itemsTobeDeleted = []
    for item, support in headerTable.items():
        if support < minSupport:
            itemsTobeDeleted.append(item)
    for item in itemsTobeDeleted:
        headerTable.pop(item)

class FPTree:
    def __init__(self,dataset, minSupport, iterator):
        self.dataset = dataset
        self.minSupport = minSupport
        self.iterator = iterator

    def createFPTree(self):
        headerTable = {}
        generateHeaderTable(headerTable, self.dataset, self.minSupport)
        self.iterator=self.iterator+1

        frequent_itemset = set(headerTable.keys())
        lengthOfFrequentItemset = len(frequent_itemset)
        if lengthOfFrequentItemset == 0:
            return None, None

        root = Node('Null Set',1)

        for k in headerTable.keys():
            headerTable[k] = [headerTable[k], None]

        for itemset,count in self.dataset.items():
            frequent_transaction = {}

            for item in itemset:
                if item in frequent_itemset:
                    frequent_transaction[item] = headerTable[item][0]
            AddToTransaction = len(frequent_transaction) >= 1
            if AddToTransaction:
                ordered_itemset = [v[0] for v in sorted(frequent_transaction.items(), key=lambda p: p[1], reverse=True)]
                self.iterator=0
                self.addTransactionToTree(ordered_itemset, root, headerTable, count , self.iterator)

        return root, headerTable


    def addNodeLink(self,startNode,targetNode,iterator):
        iterator =iterator+1
        while (startNode.nodeLink != None):
            startNode = startNode.nodeLink
        startNode.nodeLink = targetNode

    def addTransactionToTree(self, itemset, FPTree, headerTable, count ,iterator):
        if itemset[0] in FPTree.children:
            FPTree.children[itemset[0]].count=FPTree.children[itemset[0]].count+count
        else:
            FPTree.children[itemset[0]] = Node(itemset[0], count)

            if headerTable[itemset[0]][1] == None:
                headerTable[itemset[0]][1] = FPTree.children[itemset[0]]
            else:
                iterator = 0
                self.addNodeLink(headerTable[itemset[0]][1], FPTree.children[itemset[0]],iterator)

        if len(itemset) >= 2:
            self.addTransactionToTree(itemset[1::], FPTree.children[itemset[0]], headerTable, count ,iterator)

class TreeMining:
    def __init__(self,FPTree, headerTable, minSupport, prefix, frequent_itemset,closed_maximum,support_count_subset):
        self.FPTree = FPTree 
        self.headerTable = headerTable 
        self.minSupport = minSupport 
        self.prefix = prefix 
        self.frequent_itemset = frequent_itemset
        self.closed_maximum = closed_maximum 
        self.support_count_subset = support_count_subset

    def treeMining(self):

        support_count=[v[1][0] for v in sorted(self.headerTable.items(),key=lambda p: p[1][0])]
        bigL = [v[0] for v in sorted(self.headerTable.items(),key=lambda p: p[1][0])]

        conditionalDatabase={}
        mergingStrategy(conditionalDatabase,self.FPTree,"")
        all_support_counts=[]
        lengthOfBigL = len(bigL)
        for i in range(lengthOfBigL):
            bigLcurrentIterationValue = bigL[i]
            support_countItrValue = support_count[i]
            new_frequentset = self.prefix.copy()
            new_frequentset.append(bigLcurrentIterationValue)

            recursive_purpose_new_frequentset=self.prefix.copy()
            recursive_purpose_new_frequentset.append(bigLcurrentIterationValue)
            
            #add frequent itemset to final list of frequent itemsets
            self.frequent_itemset[tuple(new_frequentset)]= support_countItrValue

            

            if bigLcurrentIterationValue in conditionalDatabase:
                Conditional_pattern_bases=conditionalDatabase[bigLcurrentIterationValue]
            else:
                Conditional_pattern_bases={}

            
            all_support_counts.append(support_count[i])

            iterator=0
            fp_tree = FPTree(Conditional_pattern_bases,self.minSupport,iterator)
            Conditional_FPTree, Conditional_header = fp_tree.createFPTree()

            if Conditional_header ==None:
                self.closed_maximum[tuple(new_frequentset)]=support_countItrValue

            if Conditional_header != None:
                tp = TreeMining(Conditional_FPTree, Conditional_header, self.minSupport, recursive_purpose_new_frequentset, self.frequent_itemset,self.closed_maximum,support_count[i])
                tp.treeMining()
        
        max_support_count=0
        lengthOfMaxSupportCount = len(all_support_counts) 
        for j in range(lengthOfMaxSupportCount):
            if max_support_count< all_support_counts[j] :
                max_support_count=all_support_counts[j]

        superset_found=False

        for super_items,super_support in self.closed_maximum.items():
            if set(tuple(self.prefix)).issubset(super_items) and super_support==self.support_count_subset:
                superset_found=True

        if superset_found==False and self.support_count_subset>max_support_count:
            self.closed_maximum[tuple(self.prefix)]=self.support_count_subset


def fpgrowthFromFile(fname, minSup):
    start = time.time()
    # print(frequency)
    initSet = loadingData(fname)
    iterator=0
    # print(initSet)
    fp_tree = FPTree(initSet, minSup,iterator)
    FPtree, headerTable = fp_tree.createFPTree()
    # print(headerTable)
    frequent_itemset = {}
    closed_maximum={}
    tp = TreeMining(FPtree, headerTable, minSup, [], frequent_itemset,closed_maximum,0)
    tp.treeMining()
    end = time.time()
    print(end-start)
    return frequent_itemset, closed_maximum

if __name__ == '__main__':
    minimum_support = 1000
    print("Minimum support : ", minimum_support)
    
    freqItems, closedFreqItems = fpgrowthFromFile("../../BMS1.txt", minimum_support)
    
    print(closedFreqItems)
    

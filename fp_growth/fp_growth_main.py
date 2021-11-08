from utils import getFromFile,constructTree
from mine_tree import mineTree, associationRule

def fpgrowthFromFile(fname, minSup, minConf):
    itemSetList, frequency = getFromFile(fname)
    # print(frequency)
    
    print(minSup)
    fpTree, headerTable = constructTree(itemSetList, frequency, minSup)
    print(headerTable)
    freqItems = []
    mineTree(headerTable, minSup, set(), freqItems)
    rules = associationRule(freqItems, itemSetList, minConf)
    return freqItems, rules

if __name__ == '__main__':
    freqItems, rules = fpgrowthFromFile("../test_data.txt", 2, 0.5)
    print(freqItems)
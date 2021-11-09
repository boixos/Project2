from utils import getFromFile,constructTree
from mine_tree import mineTree, associationRule

def fpgrowthFromFile(fname, minSup, minConf):
    itemSetList, frequency = getFromFile(fname)
    # print(frequency)
    
    fpTree, headerTable = constructTree(itemSetList, frequency, minSup)
    # print(headerTable)
    freqItems = []
    closedFreqItems = []
    mineTree(headerTable, minSup, set(), freqItems, closedFreqItems)
    # rules = associationRule(freqItems, itemSetList, minConf)
    return freqItems, closedFreqItems

if __name__ == '__main__':
    freqItems, closedFreqItems = fpgrowthFromFile("../../test_data.txt", 2, 0.5)
    print(closedFreqItems)
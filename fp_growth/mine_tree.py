from collections import defaultdict
from itertools import chain, combinations
from utils import createFPTree, mergingStrategy

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

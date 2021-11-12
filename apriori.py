import pandas as pd
import numpy as np
import time
import logging
import sys
import csv
from collections import defaultdict
from itertools import chain, combinations
from math import floor
from mpi4py import MPI
from os.path import abspath, dirname, join

#running apriori using inbuilt library
from apyori import apriori


#Function to process input file to extract transactions
def process_file(filename,msup,mcon):
    f1 = open(filename,'r')
    print("Reading dataset")

    tnx = list()

    for line in f1.readlines():
        items = line.split(' -1 ')
        # if items[-1] == '-2\n':
        items.pop()
        tnx.append(items)
        # print(items)
    # print(tnx)
    itnx = set()
    for t in tnx:
        itnx.update(t)
    items = sorted(list(itnx))
    print("File reading completed")  
    return tnx,itnx      



#Hash technique
class hashTable:
    def __init__(self, hash_table_size):
        self.hash_table = [0] * hash_table_size

    def insert(self, itemset):
        # print(itemset)
        hash_index = (int(itemset[0])*10+int(itemset[1]))%7
        self.hash_table[hash_index] += 1

    def get_itemset_count(self, itemset):
        hash_index = (int(itemset[0])*10+int(itemset[1]))%7
        return self.hash_table[hash_index]
def check(candidate_itemset,level_frequent_itemsets,k):
        return all((list(_)+candidate_itemset[-2:]) in level_frequent_itemsets for _ in combinations(candidate_itemset[:-2], k-2))
def generateCandidateItemsets(k, level_frequent_itemsets):
  

        n = len(level_frequent_itemsets)

        candidate_frequent_itemsets = []
        itt = 0
        i=0
        while itt < n:
                j = i+1
                while (j<n):
                        if level_frequent_itemsets[i][:k-1] == level_frequent_itemsets[j][:k-1]:

                                cip = False
                                candidate_itemset = level_frequent_itemsets[i][:k-1] + [level_frequent_itemsets[i][k-1]] + [level_frequent_itemsets[j][k-1]]


                                if k == 1:
                                        cip = True

                                elif (k == 2):
                                        if (candidate_itemset[-2:] in level_frequent_itemsets):
                                                cip=True
                                        # cip = True

                                elif check(candidate_itemset,level_frequent_itemsets,k):
                                        cip = True

                                if cip:
                                        candidate_frequent_itemsets.append(candidate_itemset)

                                j += 1
                        else:
                                break        
                i+=1 
                itt +=1       

        return candidate_frequent_itemsets

def lfi(candidate_frequent_itemsets, candidate_freq_itemsets_cnts,min_support_count):
        lfi = []
        for i,s in zip(candidate_frequent_itemsets, candidate_freq_itemsets_cnts):
                if(s>=min_support_count):
                        lfi.append(i)
        return lfi


def sfi(candidate_frequent_itemsets, candidate_freq_itemsets_cnts,min_support_count):
        sfi = []
        for i,s in zip(candidate_frequent_itemsets, candidate_freq_itemsets_cnts):
                if(s>=min_support_count):
                        sfi.append(s)
        return sfi 


def list_helper(candidate_frequent_itemsets,frequent_itemsets,support_itemsets,candidate_freq_itemsets_cnts,min_support_count):
        rlfi = lfi(candidate_frequent_itemsets, candidate_freq_itemsets_cnts,min_support_count)
        rsfi = sfi(candidate_frequent_itemsets, candidate_freq_itemsets_cnts,min_support_count)

        frequent_itemsets.extend([set(level_frequent_itemset) for level_frequent_itemset in rlfi])
        support_itemsets.extend(s for s in rsfi)
        return rlfi


def addtohash(tnx,hash_tb,candidate_frequent_itemsets,candidate_freq_itemsets_cnts,k):
        for t in tnx:
                        # add the count of itemsets of size 2 to hashtable
                        if k == 1:
                            for itemset in combinations(t, 2):
                                hash_tb.insert(itemset)

                        for i, itm in enumerate(candidate_frequent_itemsets):
                                if all(_item in t for _item in itm):
                                        candidate_freq_itemsets_cnts[i] += 1


def aprioriAlgorithm(filename, min_support_count):

        tnx,itnx = process_file(filename,0,0)
        min_support_count = (min_support_count/100)*len(tnx)
        
        frequent_itemsets = []
        support_itemsets = []
        k = 1 # The current level number

        level_frequent_itemsets = [] # Level 0: Frequent itemsets
        support_frequent_itemsets = []
        candidate_frequent_itemsets = [[item] for item in itnx] # Level 1: Candidate itemsets

        # Intialize the hash table
        hash_tb = hashTable(7)

        for itt in range(0,2):

                # Count the support of all candidate frequent itemsets and remove transactions using transaction reduction
                candidate_freq_itemsets_cnts = [0]*len(candidate_frequent_itemsets)

                addtohash(tnx,hash_tb,candidate_frequent_itemsets,candidate_freq_itemsets_cnts,k)


               
                level_frequent_itemsets = list_helper(candidate_frequent_itemsets,frequent_itemsets,support_itemsets,candidate_freq_itemsets_cnts,min_support_count)
                
                candidate_frequent_itemsets = generateCandidateItemsets(k, level_frequent_itemsets)
                k += 1

                
                if k == 2:
                    for itemset in candidate_frequent_itemsets:
                        if hash_tb.get_itemset_count(itemset) < min_support_count:
                            print('Pruned itemset', itemset)
                            candidate_frequent_itemsets.remove(itemset)
                    # return frequent_itemsets       

        return frequent_itemsets,support_itemsets

def aprioriAlgorithmPart(itnx, min_support_count):

        # tnx,itnx = process_file(filename,0,0)
        min_support_count = (min_support_count/100)*len(itnx)
        
        frequent_itemsets = []
        support_itemsets = []
        k = 1 # The current level number

        level_frequent_itemsets = [] # Level 0: Frequent itemsets
        support_frequent_itemsets = []
        candidate_frequent_itemsets = [[item] for item in itnx] # Level 1: Candidate itemsets

        # Intialize the hash table
        hash_tb = hashTable(7)

        for itt in range(0,2):

                # Count the support of all candidate frequent itemsets and remove transactions using transaction reduction
                candidate_freq_itemsets_cnts = [0]*len(candidate_frequent_itemsets)

                addtohash(itnx,hash_tb,candidate_frequent_itemsets,candidate_freq_itemsets_cnts,k)


               
                level_frequent_itemsets = list_helper(candidate_frequent_itemsets,frequent_itemsets,support_itemsets,candidate_freq_itemsets_cnts,min_support_count)
                
                candidate_frequent_itemsets = generateCandidateItemsets(k, level_frequent_itemsets)
                k += 1

                
                if k == 2:
                    for itemset in candidate_frequent_itemsets:
                        if hash_tb.get_itemset_count(itemset) < min_support_count:
                            print('Pruned itemset', itemset)
                            candidate_frequent_itemsets.remove(itemset)
                    # return frequent_itemsets       

        return frequent_itemsets,support_itemsets

#Function to get "CLOSED FREQUENT ITEMSETS" from given frequent itemset and their suppoert count
def getcloseditemsets(frequent_itemsets,support_itemsets,min_support_count):
        for id,i in enumerate(frequent_itemsets):
                for idx,j in enumerate(frequent_itemsets):
                        if i==j:
                                continue
                        elif set(i).issubset(j) and support_itemsets[id]==support_itemsets[idx]:
                                frequent_itemsets[id] = {}
                                support_itemsets[id] = 0
        itm = list(filter(lambda x: x!={},frequent_itemsets))
        sitm = list(filter(lambda x: x!=0,support_itemsets))
        fi=[]
        si =[]

        for id,i in enumerate(itm):
                x=support_itemsets[id]
                if x>=min_support_count:
                        fi.append(i)
                        si.append(support_itemsets[id])
        print("Closed Frequent Itemsets")                
        print(fi)
        print(si)
        return fi,si
           
                                                          



############ Partitioning #################3333
def getclosedfreqpart(candidate_frequent_itemsets, candidate_freq_itemsets_cnts,global_min_support_count):
        gfi = []
        gsfi = []
        for i,s in zip(candidate_frequent_itemsets, candidate_freq_itemsets_cnts):
                if s >= global_min_support_count:
                        gfi.append(i)
                        gsfi.append(s)
        return gfi,gsfi

        global_frequent_itemsets = [itemset for itemset, support in zip(candidate_frequent_itemsets, candidate_freq_itemsets_cnts) if support >= global_min_support_count]
def __customListsReduce(new_list, reduced_list):
	''' Custom Reduce Operation that reduces two lists by taking their union '''
	for item in new_list:
		if item not in reduced_list:
			reduced_list.append(item)
	return reduced_list

def aprPart():

        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        comm_size = comm.Get_size()

        if rank == 0:
                filename = input()

                dataset_file = open(filename)
                
                n_transactions = 0
                for line in dataset_file.readlines():
                        n_transactions += 1

                print("Number of Transactions = {}".format(n_transactions))

                # Read and broadcast the min support to all processes
                min_support = int(input())
                min_support = min_support/100
                comm.bcast(min_support, root=0)

                n_trans_root = n_transactions%(comm_size-1)
                n_trans_per_worker = n_transactions//(comm_size-1)

                # Read chunks of data from file and send to each worker
                dataset_file.seek(0, 0)
                for i_process in range(1, comm_size):
                        transactions = [set(next(dataset_file).strip().split(' -1 ')) for x in range(n_trans_per_worker)]
                        # Using blocking send to avoid memory overflow in case of congested networks
                        comm.send(transactions, dest=i_process, tag=0)
                        del transactions

                # Read the chunk of data for root node
                transactions = [set(next(dataset_file).strip().split(' -1 ')) for x in range(n_trans_root)]
                local_min_support_count = floor(min_support*n_trans_root)

                local_frequent_itemsets = aprioriAlgorithmPart(transactions, local_min_support_count)


                candidate_frequent_itemsets = comm.reduce(local_frequent_itemsets, op=__customListsReduce, root=0)

                global_min_support_count = floor(min_support*n_transactions)
                candidate_freq_itemsets_cnts = [0]*len(candidate_frequent_itemsets)

                dataset_file.seek(0, 0)
                for transaction_str in dataset_file:
                        transaction = set(transaction_str.strip().split(','))
                        for i, itemset in enumerate(candidate_frequent_itemsets):
                                        if itemset <= transaction:
                                                candidate_freq_itemsets_cnts[i] += 1

                global_frequent_itemsets,support_frequent_itemsets = getclosedfreqpart(candidate_frequent_itemsets, candidate_freq_itemsets_cnts,global_min_support_count)
                global_frequent_itemsets,support_frequent_itemsets = getcloseditemsets(global_frequent_itemsets,support_frequent_itemsets,min_support_count)
                
                print(global_frequent_itemsets)
                print(support_frequent_itemsets)

        else:
                min_support = comm.bcast(None, root=0)
                transactions = comm.recv(source=0, tag=0)

                worker_n_trans = len(transactions)
                local_min_support_count = floor(min_support*worker_n_trans)

                
                local_frequent_itemsets = aprioriAlgorithm(transactions, local_min_support_count)


                comm.reduce(local_frequent_itemsets, op=__customListsReduce, root=0)


if __name__ == '__main__':


        print("Enter File Name")
        filename = input()
        # transactions = process_file(filename,0,0) 
        # freqitemsets,t1,t2=apriori_improvised_partitions(transactions,5,0.70,0.50)
        # association_rules=find_rules_partitioned(len(transactions),freqitemsets,0.50,0.70)
        # for i in association_rules:
        #     print("Rule Number ",c," :",i[0]," -> ",i[1])
        #     c=c+1
        x = int(input())     
        min_support_count = x
        st = time.time()
        # # Generate list of all frequent itemsets using Transaction Reduction based Apriori
        frequent_itemsets,support_itemsets = aprioriAlgorithm(filename, min_support_count)
        end = time.time()
        getcloseditemsets(frequent_itemsets,support_itemsets,min_support_count)
        print("\nFREQUENT ITEMSETS (Min Support Count = {})".format(1190))
        print("Freq itemsets")
        print(frequent_itemsets)
        print("support of above itemsets")
        print(support_itemsets)
        t = end-st
        print(t)
        aprPart()   #####Partitioning

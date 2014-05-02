#! /usr/bin/env python2.7

import argparse
import os
import json
import csv
import sys
import itertools
from operator import *

temp_name_list = "./temp_name_list"
temp_transactions_list = "./temp_transactions_list"
csv_delimiter=','
output_file_path = "./output.txt"


# in this function, we read the CSV file, and give each element in the CSV file a index number
# thus reducing the total memory usage and give better performance than processing long string

def processCSV(file_path,debug):
#output the hash table
#and return the encoded transactions 
    if debug:
        print "*" * 10
        print sys._getframe().f_code.co_name
        print "*" * 10
    transactions = list()
    name_list = list()
    hash_count = dict()
    hash_dict = dict()
    transactions_count = 0
    count = 0
    with open(file_path,"r") as csv_input:
        raw_transactions = csv.reader(csv_input,delimiter=csv_delimiter,quotechar='"')
#by this loop, we convert each unique string to an unique integer
        for raw_row in raw_transactions:
            processed_raw = list()
            transactions_count += 1
            for element in raw_row:
                if element in hash_dict:
                    processed_raw.append(hash_dict[element])
                    hash_count[hash_dict[element]] += 1
                else:
                    processed_raw.append(str(count))
                    name_list.append(element)
                    hash_count[str(count)] = 1
                    hash_dict[element] = str(count)
                    count +=1
            transactions.append(sorted(set(processed_raw)))
    if debug:
        print name_list
        print hash_count
        print hash_dict
        print transactions

    # we output the temporary file as the index mapping an integer to its real string
    # when the program finishes, we delete this file
    with open(temp_name_list,"w") as output_name_list:
        json.dump(name_list,output_name_list)

    return (transactions,hash_count,count,transactions_count)


# the entry of getting the frequent itemsets
def genFrequentItemsets(transactions,hash_count,count,transactions_count,min_sup,debug):
# what we need, a candidate list, a transaction list and a count
    if debug:
        print "*" * 10
        print sys._getframe().f_code.co_name
        print "*" * 10
    frequent_list = list()
    hash_count_all = list()

    frequent_0 = list()

# the first round
#processing the first single element group
# count is the total number of items, and we start from the lowest number of the item, then every time during the iteration, we can keep the property that the itemset is sorted, without further sort. 
    for i in xrange(count):
        if debug:
            print i
            print hash_count[str(i)]  
            print min_sup*transactions_count
            print min_sup
            print transactions_count
        if hash_count[str(i)] >= min_sup*transactions_count:
            frequent_0.append(([str(i)],str(i)))
        else:
            hash_count.pop(str(i),None)
    frequent_list.append(frequent_0)
    hash_count_all.append(hash_count)
    p_hash_count = hash_count
    p_itemsets = frequent_0
#        if debug:
#            print p_itemsets
    if not len(frequent_0):
        return (0,None,None)
    k = 1
    while True:
#start iteration
        p_hash_count,p_itemsets = genSizeKFrequentItemsets(k,p_itemsets,p_hash_count,transactions,transactions_count,min_sup,debug)
        if len(p_itemsets):
            frequent_list.append(p_itemsets)
            hash_count_all.append(p_hash_count)
        else:
            break
        k += 1
        #break
    return (k,frequent_list,hash_count_all)


def genSizeKFrequentItemsets(k,p_itemsets,p_hash_count,transactions,transactions_count,min_sup,debug):
    if debug:
        print "*" * 10
        print sys._getframe().f_code.co_name
        print "*" * 10
    cur_hash_count = dict()
    cur_itemsets = list()
    length = len(p_itemsets)
#for each pair of the itemsets in previous iteration, we combine them if they can be combined
# and for each itemsets in the previous set is sorted, then we do not need to sort them, every time the combination will give you another sorted itemset, as well as the total list of itemsets.
    #print p_hash_count
    for i in xrange(length-1):
        for j in xrange(i+1,length):
            temp_tuple = None
# if this is the first iteration, we don't need to compare anything
            if k==1:
                temp_list = [p_itemsets[i][0][0],p_itemsets[j][0][0]]
                temp_tuple = (temp_list,",".join(temp_list),set(temp_list),p_itemsets[i][0][0])

# then we store each k-1 string in the 2 position of the itemsets tuple, then we can just compare them in O(1) time
# for python treat each string as a constant
            else:
# if two itemsets with length k are equal in their previous k-1 position, then we combine them to a new one, and note that in the sequence of our insertion value start from the smaller sequence, then we can ensure that p_itemsets[j][0][-1] has a larger index element
                if p_itemsets[i][2] == p_itemsets[j][2]:
                    temp_list = list(p_itemsets[i][0])
                    temp_list.append(p_itemsets[j][0][-1])
                    temp_tuple = (temp_list,",".join(temp_list),set(temp_list),",".join(temp_list[:-1]))
            # prune
# then we need to do the pruning
            if temp_tuple is not None:
                flag = True
# we use the itertools to get the combinations of k elements in our new k+1 itemsets, if one of these substring is not in the previous hash_count structure(which only contains frequent item larger than the min_support) then we think this tuple is not eligible.
# the most important property is that the combinations function won't disrupt the order of our element in the itemset, then we can ensure that the one of the combination string is in our hash table if and only if the set exceeds the min support 
                for ele in itertools.combinations(temp_tuple[0],len(temp_tuple[0])-1):
                    if debug:
                        print temp_tuple
                        print ele
                        print ",".join(ele)
                    if ",".join(ele) not in p_hash_count:
                        flag = False
                        break
                if flag == True:
                    cur_itemsets.append(temp_tuple)
                    cur_hash_count[cur_itemsets[-1][1]] = 0

# then we use transaction to construct the new hash count
# this time we use the data structure called set in the python, it provides the convenient function issubset to determine whether a set is the subset of another one.
    #print p_hash_count
    #raw_input()
    for transaction in transactions:
        temp_transaction = set(transaction)
        for element in cur_itemsets:
            if debug:
                pass
                #print element
                #raw_input()
            #print "haha"
            if element[2].issubset(temp_transaction) == True:
                cur_hash_count[element[1]] += 1

    if debug:
		print cur_hash_count

    cur_itemsets_final = list()
# then we filter out those itemsets lower than the threshold
    for ele in cur_itemsets:
        if cur_hash_count[ele[1]] < min_sup*transactions_count:
            cur_hash_count.pop(ele[1],None)
        else:
            cur_itemsets_final.append((ele[0],ele[1],ele[3]))

    if debug:
        print cur_hash_count

    if debug:
        print "*"*10
        print k
        print cur_itemsets_final
        print cur_hash_count
        print "*"*10

    return (cur_hash_count,cur_itemsets_final)



def genAssociateRule(k,frequent_list,hash_count_all,transactions_count,min_conf,debug):

    if debug:
        print "*" * 10
        print sys._getframe().f_code.co_name
        print "*" * 10
    output_file = open(output_file_path,"a") 
    output_file.write("\n\n\n")
    print "==High-confidence association rules (min_conf=%s)"%('{:.2%}'.format(min_conf))
    output_file.write("==High-confidence association rules (min_conf=%s)\n"%('{:.2%}'.format(min_conf)))
   # if there isn't any even length 2 itemsets, then it will be no associate rule
    if k == 1 or k == 0:
        print "Not Any Associate Rule Found With The Given Min Confidence"
        output_file.write("Not Any Associate Rule Found With The Given Min Confidence\n")
        print "Soooooooooooo  Sad"
        output_file.write("Soooooooooooo  Sad")
    else:
# open the file with the original string information
        name_input = open(temp_name_list,"r")
        name_list = json.load(name_input)
        if debug:
            print name_list
        associate_rule_out_put_list = list()
# generate each length's itemsets's associate rules
        for i in xrange(1,k):
        # iterate each elements in the L\_i
            for frequent_item in frequent_list[i]:
                # iterate each possible rule
                for j in xrange(i+1):
                    if j==0:
                        hash_string = ",".join(frequent_item[0][1:])
                    else:
                        hash_string = ",".join(frequent_item[0][:j])
                        if debug:
                            print i
                            print j
                            print frequent_item[0]
                        try:
                            if i != 1:
                                if j+1 <= i:
                                    hash_string = hash_string+","+",".join(frequent_item[0][j+1:])
                        except:
                            print "error"
                            pass
                    if debug:
                        print hash_string
# refer the hash count table to find the count(support)
                    sup = hash_count_all[i][frequent_item[1]]
                    sup2 = (hash_count_all[i-1][hash_string])
# filter with mini conf
                    if float(sup) / (sup2) >= min_conf:
                        if debug:
                            print sup
                            print sup2
                        #print "An Associate Rule Found"
                        temp_list = list()
                        for k in xrange(i+1):
                            if k != j:
                                temp_list.append(name_list[int(frequent_item[0][k])])
                        if debug:
                            print temp_list
                            print frequent_item
#                        print "[%s] =====> %s (Conf:%s,Supp:%s)"%(",".join(temp_list),name_list[int(frequent_item[0][j])],'{:.2%}'.format(float(sup)/sup2),'{:.2%}'.format(float(sup)/transactions_count))
                        associate_rule_out_put_list.append(("[%s] =====> [%s] (Conf:%s,Supp:%s)"%(",".join(temp_list),name_list[int(frequent_item[0][j])],'{:.2%}'.format(float(sup)/sup2),'{:.2%}'.format(float(sup)/transactions_count)),float(sup)/sup2,float(sup)/transactions_count))
                            
        associate_rule_out_put_list = sorted(associate_rule_out_put_list,key=itemgetter(1,2),reverse=True)
        for associate_rule in associate_rule_out_put_list:
            print associate_rule[0]
            output_file.write(associate_rule[0]+"\n")
        

def displayFrequentItems(k,frequent_list,hash_count_all,transactions_count,min_sup,debug):
    if debug:
        print "*" * 10
        print sys._getframe().f_code.co_name
        print "*" * 10
    output_file = open(output_file_path,"a") 
    print "==Frequent itemsets (min_sup=%s)"%('{:.2%}'.format(min_sup))
    output_file.write("==Frequent itemsets (min_sup=%s)\n"%('{:.2%}'.format(min_sup)))
    if not k:
        print "Sooooooooooooooooo Sad"
        output_file.write("Sooooooooooooooooo Sad\n")
        print "Not Any Frequent Items Found What The Stupid Dataset You Are Using?"
        output_file.write("Not Any Frequent Items Found What The Stupid Dataset You Are Using?\n")
    else:
# open the file with the original string information
        name_input = open(temp_name_list,"r")
        name_list = json.load(name_input)
        frequent_item_out_put_list = list()
# generate each length's itemsets's frequent list
        for i in xrange(k):
        # iterate each elements in the L\_i
            for frequent_item in frequent_list[i]:
                sup = hash_count_all[i][frequent_item[1]]
                temp_list = list()
            # look up the original string information to build the output string 
                for ele in frequent_item[0]:
                    temp_list.append(name_list[int(ele)])
                frequent_item_out_put_list.append(("[%s],%s"%(",".join(temp_list),'{:.2%}'.format(float(sup)/transactions_count)),float(sup)/transactions_count))
        frequent_item_out_put_list = sorted(frequent_item_out_put_list,key=itemgetter(1),reverse=True)
        for frequent_item in frequent_item_out_put_list:
            print frequent_item[0]
            output_file.write(frequent_item[0]+"\n")
                    


def clean():
    if os.path.exists(temp_name_list):
        os.remove(temp_name_list)
    if os.path.exists(temp_transactions_list):
        os.remove(temp_transactions_list)



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i","--input",type=str,dest="file_path",required=True)
    parser.add_argument("-d","--debug",type=int,dest="debug",default=0)
    parser.add_argument("-s","--minsup",type=float,dest="min_sup",default=0.75)
    parser.add_argument("-c","--minconf",type=float,dest="min_conf",default=0.8)
    #parser.add_argument("--delimiter",type=str,dest="delimiter",default=csv_delimiter)
    args = parser.parse_args()
    transactions,hash_count,count,transactions_count=processCSV(args.file_path,args.debug)
    k,frequent_list,hash_count_all=genFrequentItemsets(transactions,hash_count,count,transactions_count,args.min_sup,args.debug)
    if os.path.exists(output_file_path):
        os.remove(output_file_path)
    if args.debug:
        print k
        print frequent_list
        print hash_count_all
        print transactions_count
    displayFrequentItems(k,frequent_list,hash_count_all,transactions_count,args.min_sup,args.debug)
    genAssociateRule(k,frequent_list,hash_count_all,transactions_count,args.min_conf,args.debug)
    if not args.debug:
        clean()


if __name__=="__main__":
    main()

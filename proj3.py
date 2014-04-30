#! /usr/bin/env python2.7

import argparse
import os
import json
import csv
import sys
import itertools

temp_name_list = "./temp_name_list"
temp_transactions_list = "./temp_transactions_list"
csv_delimiter='^'


# in this function, we read the CSV file, and give each element in the CSV file a index number

def processCSV(file_path,debug,large):
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
        for raw_row in raw_transactions:
            processed_raw = list()
            transactions_count += 1
            row = map(lambda x:x.lower(),raw_row)
            for element in row:
                if element.lower() in hash_dict:
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
    
    with open(temp_name_list,"w") as output_name_list:
        json.dump(name_list,output_name_list)

    if large:
        with open(temp_transactions_list,"w") as output_transaction_list:
            json.dump(transactions,output_transaction_list)
        return (None,hash_count,count,transactions_count)
    return (transactions,hash_count,count,transactions_count)



def genFrequentItemsets(transactions,hash_count,count,transactions_count,large,min_sup,debug):
# what we need, a candidate list, a transaction list and a count
    if debug:
        print "*" * 10
        print sys._getframe().f_code.co_name
        print "*" * 10
    frequent_list = list()
    hash_count_all = list()
    hash_count_all.append(hash_count)
# if we cannot place things in the memory then we store every mid-result in the file
    if large:
        pass
    else:
# the first round
        frequent_0 = list()
        for i in xrange(count):
            if hash_count[str(i)] >= min_sup*transactions_count:
                frequent_0.append(([str(i)],str(i)))
        frequent_list.append(frequent_0)
        p_hash_count = hash_count
        p_itemsets = frequent_0
#        if debug:
#            print p_itemsets
        if not len(frequent_0):
            return (0,None,None)
        k = 1
        while True:
            p_hash_count,p_itemsets = genSizeKFrequentItemsets(k,p_itemsets,p_hash_count,transactions,transactions_count,large,min_sup,debug)
            if len(p_itemsets):
                frequent_list.append(p_itemsets)
                hash_count_all.append(p_hash_count)
            else:
                break
            k += 1
            #break
    return (k,frequent_list,hash_count_all)


def genSizeKFrequentItemsets(k,p_itemsets,p_hash_count,transactions,transactions_count,large,min_sup,debug):
    if debug:
        print "*" * 10
        print sys._getframe().f_code.co_name
        print "*" * 10
    cur_hash_count = dict()
    cur_itemsets = list()
    if large:
        pass
    else:
        length = len(p_itemsets)
#        if debug:
#            print length
        #gen new candidates
        for i in xrange(length-1):
            for j in xrange(i+1,length):
#                if debug:
#                    print i
#                    print j
                temp_tuple = None
                if k==1:
                    temp_list = [str(i),str(j)]
                    temp_tuple = (temp_list,",".join(temp_list),set(temp_list),str(i))
                else:
                    if p_itemsets[i][2] == p_itemsets[j][2]:
#                        if debug:
#                            print p_itemsets[i][0]
#                            print p_itemsets[j][0]
#                            print p_itemsets[j][0][-1]
                        temp_list = list(p_itemsets[i][0])
                        temp_list.append(p_itemsets[j][0][-1])
#                        if debug:
#                            print temp_list
                        temp_tuple = (temp_list,",".join(temp_list),set(temp_list),",".join(temp_list[:-1]))
                # prune
                if temp_tuple is not None:
                    flag = True
                    for ele in itertools.combinations(temp_tuple[0],len(temp_tuple[0])-1):
                        if ",".join(ele) not in p_hash_count:
                            flag = False
                            break
                    if flag == True:
                        cur_itemsets.append(temp_tuple)
                        cur_hash_count[cur_itemsets[-1][1]] = 0

        for transaction in transactions:
#            if debug:
#                print transaction
            temp_transaction = set(transaction)
            for element in cur_itemsets:
                if element[2].issubset(temp_transaction) == True:
                    cur_hash_count[element[1]] += 1

        if debug:
            print cur_hash_count
        cur_itemsets_final = list()
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



def genAssociateRule(k,frequent_list,hash_count_all,transactions_count,large,min_conf,debug):
    if debug:
        print "*" * 10
        print sys._getframe().f_code.co_name
        print "*" * 10
    print "==High-confidence association rules (min_conf=%s)"%('{:.2%}'.format(min_conf))
    if k == 1 or k == 0:
        print "Not Any Associate Rule Found With The Given Min Confidence"
        print "Soooooooooooo  Sad"
    else:
        name_input = open(temp_name_list,"r")
        name_list = json.load(name_input)
        if debug:
            print name_list
        if large:
            pass
        else:
            for i in xrange(1,k):
                for frequent_item in frequent_list[i]:
                    for j in xrange(i+1):
                        if j==0:
                            hash_string = ",".join(frequent_item[0][1:])
                        else:
                            hash_string = ",".join(frequent_item[0][:j])
                            try:
                                if i != 1:
                                    hash_string = hash_string+","+",".join(frequent_item[0][j+1:])
                            except:
                                pass
                        if debug:
                            print hash_string
                        sup = hash_count_all[i][frequent_item[1]]
                        sup2 = (hash_count_all[i-1][hash_string])
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
                            print "[%s] =====> %s (Conf:%s,Supp:%s)"%(",".join(temp_list),name_list[int(frequent_item[0][j])],'{:.2%}'.format(float(sup)/sup2),'{:.2%}'.format(float(sup2)/transactions_count))
                            

    return None

def displayFrequentItems(k,frequent_list,hash_count_all,transactions_count,large,min_sup,debug):
    if debug:
        print "*" * 10
        print sys._getframe().f_code.co_name
        print "*" * 10
    print "==Frequent itemsets (min_sup=%s)"%('{:.2%}'.format(min_sup))
    if not k:
        print "Sooooooooooooooooo Sad"
        print "Not Any Frequent Items Found What The Stupid Dataset You Are Using?"
    if large:
        pass
    else:
        name_input = open(temp_name_list,"r")
        name_list = json.load(name_input)
        if debug:
            print name_list
        for i in xrange(k):
            for frequent_item in frequent_list[i]:
                sup = hash_count_all[i][frequent_item[1]]
                temp_list = list()
                for ele in frequent_item[0]:
                    temp_list.append(name_list[int(ele)])
                    print "[%s],%s"%(",".join(temp_list),'{:.2%}'.format(float(sup)/transactions_count))


def clean():
    if os.path.exists(temp_name_list):
        os.remove(temp_name_list)
    if os.path.exists(temp_transactions_list):
        os.remove(temp_transactions_list)



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i","--input",type=str,dest="file_path",required=True)
    parser.add_argument("-d","--debug",type=int,dest="debug",default=0)
    parser.add_argument("-l","--large",type=int,dest="large",default=0)
    parser.add_argument("-s","--minsup",type=float,dest="min_sup",default=0.75)
    parser.add_argument("-c","--minconf",type=float,dest="min_conf",default=0.8)
    parser.add_argument("--delimiter",type=str,dest="delimiter",default=csv_delimiter)
    args = parser.parse_args()
    transactions,hash_count,count,transactions_count=processCSV(args.file_path,args.debug,args.large)
    k,frequent_list,hash_count_all=genFrequentItemsets(transactions,hash_count,count,transactions_count,args.large,args.min_sup,args.debug)
    if args.debug:
        print k
        print frequent_list
        print hash_count_all
    displayFrequentItems(k,frequent_list,hash_count_all,transactions_count,args.large,args.min_sup,args.debug)
    associate_rule = genAssociateRule(k,frequent_list,hash_count_all,transactions_count,args.large,args.min_conf,args.debug)
    if not args.debug:
        clean()


if __name__=="__main__":
    main()

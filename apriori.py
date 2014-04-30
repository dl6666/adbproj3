import csv
import sys
import math
import marshal
import operator

def readCsv(csv_file):
    with open(csv_file, 'rb') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=' ')
        transactions = []
        for row in spamreader:
            transaction = set(row[0].split(','))
            transactions.append(transaction);
#         for t in transactions:
#             for item in t:
#                 sys.stdout.write(item+' ')
#             sys.stdout.write('\n');
    return transactions


def generateSupportSets2(transactions,min_sup):
    C=[]
    sup_dict = {}
    # Add itemsets with length 1
    C.append([])
    for transaction in transactions:
        for item in transaction:
            s=[item];
            if(frozenset(s) in sup_dict.keys()):
                sup_dict[frozenset(s)] += 1
            else:
                sup_dict[frozenset(s)] = 1
                C[0].append(s)
    C[0][:] = [s for s in C[0] if (sup_dict[frozenset(s)]>=min_sup)]
    C[0] = sorted(C[0],key=operator.itemgetter(0))
     
    # Add itemsets to C_k in increasing length
    k=1
    while(k<=len(C)):
        C.append([])
        for i in range(0,len(C[k-1])-1):
            cur_set =  C[k-1][i]
            cur_subset = C[k-1][i][0:-1]
            for j in range(i+1,len(C[k-1])):
                iter_set = C[k-1][j]
                if(set(cur_subset) == set(iter_set[0:-1])):
                    next_set = list(iter_set)
                    next_set.append(cur_set[-1])
                    next_set = sorted(next_set)
                    C[k].append(next_set)
                    sup_dict[frozenset(next_set)]=0
         
        for transaction in transactions:
            for s in C[k]:
                if(set(s).issubset(transaction)):
                    sup_dict[frozenset(s)]+=1
        
#         print sup_dict
        # Prune the C_k by min_sup
        C[k][:] = [s for s in C[k] if (sup_dict[frozenset(s)]>=min_sup)]
                      
        if(len(C[k])==0):
            C.pop()
             
        k+=1
             
    return C,sup_dict

def generateOneRHSRules2(C,sup_dict,min_conf):
    R = {}
    # Generate all rules 
    for i in range(1,len(C)):
        for cur_set in C[i]:
            sup_cur = sup_dict[frozenset(cur_set)]
            for item in cur_set:
                subset = list(cur_set)
                subset.remove(item)
                sup_sub = sup_dict[frozenset(subset)]
                conf = sup_cur*1.0/sup_sub
                if(conf>=min_conf):
#                     key = str(subset)+" => "+str([item])+' '+str(sup_cur)+' '+str(sup_sub)
                    key = str(subset)+" => "+str([item])
                    R[key] = conf
    return R
    
def main():
    transactions = readCsv('restaurant.csv')
    min_sup = math.ceil(0.01*len(transactions))
    min_conf = 0.3
    
    sys.stdout.write("Support: %d\n" % min_sup)
    C2,sup_dict = generateSupportSets2(transactions,min_sup)
#     for c in C2:
#         for l in c:
#             print l
    R2 = generateOneRHSRules2(C2,sup_dict,min_conf);
    print sorted(R2.items(),key=operator.itemgetter(0))
    
if __name__ == '__main__':
    main()

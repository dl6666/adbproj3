#! /usr/bin/env python2.7

import argparse
import os
import json
import csv
import sys
import itertools
from datetime import datetime
import time

csv_delimiter=','
default_output_file_path = "./output.csv"
default_max_rows = 10000


# we use this global dict to specify which column we want
interest_columns_dict = {
    #"0": "Unique Key", 
    "97": ["Solve Time",1,2], 
    "98": ["Season",1], 
    "3": "Agency", 
    "5": "Complaint Type", 
    "7": "Location Type", 
    "23": "Borough", 
}



#we pre-process the data from the 311_Service_Requests_for_2008.csv from New York City Data Sets to generate the csv data to do the data mining, the whole data set is too large, then we just take out a part of it and process every column to extract what we want.

def processCSV(input_file_path,output_file_path,max_rows,null_filter,debug):
#output the hash table
#and return the encoded transactions 
    if debug:
        print "*" * 10
        print sys._getframe().f_code.co_name
        print "*" * 10
    count = 0
    line = 0
    output_csv_file = open(output_file_path,"wb")
    output_csv_write = csv.writer(output_csv_file,delimiter=csv_delimiter,quotechar='"')
# open the csv file
    with open(input_file_path,"rU") as csv_input:
        raw_transactions = csv.reader(csv_input,delimiter=csv_delimiter,quotechar='"',dialect=csv.excel_tab)
        head = raw_transactions.next()
        print head
        out_put_dict = dict()
        head_count = 0
        for element in head:
            out_put_dict[head_count] = element
            head_count += 1
        # output the head column of the csv file
        with open("./csv_head","w") as out_head:
            json.dump(out_put_dict,out_head,indent = 4)

        
        for raw_row in raw_transactions:
            if count > max_rows:
                break
            #every 20 rows we sample one 
            if line%20 == 0:
                processed_row = list()
                flag = True
                for key in interest_columns_dict.keys():
# process date
                    int_key = int(key)
# compute the solve time
                    if int_key==97:
                        if raw_row[interest_columns_dict[key][1]] != '' and raw_row[interest_columns_dict[key][2]] != '': 
                            #print raw_row[1]
                            #print raw_row[2]
                            delta_days=int((datetime.strptime(raw_row[interest_columns_dict[key][2]],"%m/%d/%Y %I:%M:%S %p") - datetime.strptime(raw_row[interest_columns_dict[key][1]],"%m/%d/%Y %I:%M:%S %p")).days)
                            prefix = interest_columns_dict[key][0]
                            if delta_days <= 0:
                                processed_row.append(prefix+':same day')
                            elif delta_days < 7:
                                processed_row.append(prefix+':less than 1 week')
                            elif delta_days >= 30:
                                processed_row.append(prefix+':more than 1 month')
                            elif delta_days >= 7:
                                processed_row.append(prefix+':more than 1 week')
                            #print time.strptime("%m/%d/%y %H:%M","0"+raw_row[1])
                            #raw_input()
                        else:
                            processed_row.append('')
# compute the event occurrence month
                    elif int_key==98:
                        if raw_row[interest_columns_dict[key][1]] != '' :
                            prefix = interest_columns_dict[key][0]
                            month = datetime.strptime(raw_row[interest_columns_dict[key][1]],"%m/%d/%Y %I:%M:%S %p")
                            month = month.month
                            processed_row.append(prefix+":%s"%(str(month)))
                        else:
                            processed_row.append('')
# compute the event occurrence day time period
                    elif int_key == 99:
                        if raw_row[interest_columns_dict[key][1]] != '' :
                            prefix = interest_columns_dict[key][0]
                            hour = datetime.strptime(raw_row[interest_columns_dict[key][1]],"%m/%d/%Y %I:%M:%S %p")
                            hour = hour.hour 
                            if hour < 5: 
                                processed_row.append(prefix+":Midnight")
                            elif hour < 18:
                                processed_row.append(prefix+":Daytime")
                            else:
                                processed_row.append(prefix+":Evening")
                        else:
                            processed_row.append('')
# Unspecified and '' are both meaning less
                    elif int_key == 23:
                        if len(raw_row[int_key]) and raw_row[int_key] != "Unspecified":
                            processed_row.append(interest_columns_dict[key]+":"+raw_row[int_key])
                        else:
                            processed_row.append('')
                    else:
                        if len(raw_row[int_key]):
                            processed_row.append(interest_columns_dict[key]+":"+raw_row[int_key])
                        else:
                            processed_row.append('')
                    if debug:
                        print processed_row
                        #raw_input()

                if debug:
                    print processed_row
                    raw_input()
                
               # the different operation for null-contained row 
                if '' in processed_row:
                    if debug:
                        print "null field found"
                        print processed_row
                    if null_filter:
                        flag = False
                    else:
                        processed_row = [item for item in processed_row if len(item) != 0]
                    if debug:
                        print processed_row
                        raw_input()

                if flag == True:
                    if debug:
                        print "eligible field found"
                        print processed_row
                    output_csv_write.writerow(processed_row)
                    count += 1
            else:
                pass
            line += 1
        output_csv_file.close()
                      



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i","--input",type=str,dest="input_file_path",required=True)
    parser.add_argument("-o","--output",type=str,dest="output_file_path",default=default_output_file_path)
    parser.add_argument("-m","--maxrows",type=int,dest="max_rows",default=default_max_rows)
    parser.add_argument("-f","--filter",type=int,dest="null_filter",default=0,choices=[0,1],help="enable this option will let the program ignore all the rows that contain any null field")
    parser.add_argument("-d","--debug",type=int,dest="debug",default=0,choices=[0,1])
    parser.add_argument("--delimiter",type=str,dest="delimiter",default=csv_delimiter,choices=[',','^','#'])
    args = parser.parse_args()
    if args.max_rows <= 0:
        raise ValueError("max rows must be a Integer larger than 0")
    processCSV(args.input_file_path,args.output_file_path,args.max_rows,args.null_filter,args.debug)


if __name__=="__main__":
    main()

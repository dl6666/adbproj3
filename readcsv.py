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
interest_columns_index=[1,3,4,5,6,7,8,16]
interest_columns_dict={
        1:"Date",
        #3:"Agency",
        #4:"Agency Name",
        5:"Complaint Type",
        #6:"Descriptor",
        #7:"Location Type", 
        #8:"Incident Zip",
        16:"City"
        }


"""
the first several column of the original csv file is as follows
['Unique Key', 'Created Date', 'Closed Date', 'Agency', 'Agency Name', 'Complaint Type', 'Descriptor', 'Location Type', 'Incident Zip', 'Incident Address', 'Street Name', 'Cross Street 1', 'Cross Street 2', 'Intersection Street 1', 'Intersection Street 2', 'Address Type', 'City', 'Landmark', 'Facility Type']
we want Combine Created Date,Close Date to be a affair length count as days [1,2]
Agency [3]
Agency Name [4]
Complaint Type [5]
Descriptor [6] this field can be regarded as a descant of the Complaint Type
Location Type [7] What 
Incident Zip [8]
City [16]
"""


#we pre-process the data from the 311_Service_Requests_for_2008.csv from New York City Data Sets to generate the csv data to do the data mining, the whole data set is too large, then we just take out a part of it and process every column to extract what we want.

def processCSV(input_file_path,output_file_path,max_rows,null_filter,debug):
#output the hash table
#and return the encoded transactions 
    if debug:
        print "*" * 10
        print sys._getframe().f_code.co_name
        print "*" * 10
    count = 0
    output_csv_file = open(output_file_path,"wb")
    output_csv_write = csv.writer(output_csv_file,delimiter=csv_delimiter,quotechar='"')
    with open(input_file_path,"rU") as csv_input:
        raw_transactions = csv.reader(csv_input,delimiter=csv_delimiter,quotechar='"',dialect=csv.excel_tab)
        head = raw_transactions.next()
        print head
        #raw_input()
        for raw_row in raw_transactions:
            if count > max_rows:
                break
            if debug:
                print raw_row
            #raw_input()
            processed_row = list()
            flag = True
            for key in interest_columns_dict.keys():
# process date
                if key == 1:
                    if raw_row[1] != '' and raw_row[2] != '': 
                        #print raw_row[1]
                        #print raw_row[2]
                        delta_days=int((datetime.strptime(raw_row[2],"%m/%d/%y %H:%M") - datetime.strptime(raw_row[1],"%m/%d/%y %H:%M")).days)
                        if debug:
                            print delta_days
                        if delta_days <= 1:
                            processed_row.append('less than 1 day')
                        elif delta_days <=5:
                            processed_row.append('less than 5 days')
                        elif delta_days <=10:
                            processed_row.append('less than 10 days')
                        elif delta_days <=20:
                            processed_row.append('less than 20 days')
                        elif delta_days <=30:
                            processed_row.append('less than 1 month')
                        else:
                            processed_row.append('longer than 1 month')
                        #print time.strptime("%m/%d/%y %H:%M","0"+raw_row[1])
                        #raw_input()
                    else:
                        processed_row.append('')
                else:
                    processed_row.append(raw_row[key])
            
            if null_filter:
                if '' in processed_row:
                    if debug:
                        print "null field found"
                    flag = False
            if flag == True:
                if debug:
                    print "eligible field found"
                    print processed_row
                output_csv_write.writerow(processed_row)
                count += 1
        output_csv_file.close()
                      



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i","--input",type=str,dest="input_file_path",required=True)
    parser.add_argument("-o","--output",type=str,dest="output_file_path",default=default_output_file_path)
    parser.add_argument("-m","--maxrows",type=int,dest="max_rows",default=default_max_rows)
    parser.add_argument("-f","--filter",type=int,dest="null_filter",default=1,choices=[0,1],help="enable this option will let the program ignore all the rows that contain any null field")
    parser.add_argument("-d","--debug",type=int,dest="debug",default=0,choices=[0,1])
    parser.add_argument("--delimiter",type=str,dest="delimiter",default=csv_delimiter,choices=[',','^','#'])
    args = parser.parse_args()
    if args.max_rows <= 0:
        raise ValueError("max rows must be a Integer larger than 0")
    processCSV(args.input_file_path,args.output_file_path,args.max_rows,args.null_filter,args.debug)


if __name__=="__main__":
    main()

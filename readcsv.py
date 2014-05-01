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


"""
interest_columns_dict={
        1:"Date",
        #3:"Agency",
        4:"Agency Name",
        5:"Complaint Type",
        6:"Descriptor",
        7:"Location Type", 
        #8:"Incident Zip",
        16:"City"
        }


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

interest_columns_dict = {
    #"0": "Project Name", 
    #"1": "Project Description", 
    #"2": "Stimulus Tracker ID", 
    "3": "Funding Category", 
    "4": "Funding Source", 
    #"5": "Stimulus Funding", 
    #"6": "Displaced City Funding", 
    #"7": "All Other Funding", 
    #"8": "Award Lead City Agency", 
    "9": "Project Lead City Agency", 
    "10": "Project Status", 
    #"11": "% of Funds Spent", 
    #"12": "Date Funds Awarded by Fed/State", 
    #"13": "Date Funds Announced by NYC", 
    "14": ["Start Delay",14,15], 
    #"15": "Actual Start Date", 
    #"16": "Actual Completion Date", 
    #"17": "Interim Spending Deadline", 
    #"18": "% of Funds to be Spent by Interim Spending Deadine", 
    #"19": "Final Spending Deadline", 
    "20": "Contract Name", 
    "21": "Contract Method", 
    "22": "Contract Status", 
    #"23": "Contract ID #", 
    "24": "Vendor Name", 
    #"25": "Conttract Start Date", 
    #"26": "Contract End Date", 
    "27": "New or Existing Contract", 
    #"28": "Revised Contract Start Date", 
    #"29": "Revised Contract End Date", 
    #"30": "Contract Value", 
    "31": "Payment Recipient", 
    "32": "Payment Type", 
    #"33": "Payment Date", 
    "34": "Payment Description", 
    #"35": "Payment Id", 
    #"36": "Payment Value"
}



"""


interest_columns_dict={
        1:"Date",
        3:"Agency",
        4:"Agency Name",
        5:"Complaint Type",
        6:"Descriptor",
        7:"Location Type", 
        #8:"Incident Zip",
        16:"City"
        1:"Date",
        #3:"Agency",
        4:"Agency Name",
        5:"Complaint Type",
        6:"Descriptor",
        7:"Location Type", 
        #8:"Incident Zip",
        16:"City"
        }


the first several column of the original csv file is as follows

['Project Name', 'Project Description', 'Stimulus Tracker ID', 'Funding Category', 'Funding Source', 'Stimulus Funding', 'Displaced City Funding', 'All Other Funding', 'Award Lead City Agency', 'Project Lead City Agency', 'Project Status', '% of Funds Spent', 'Date Funds Awarded by Fed/State', 'Date Funds Announced by NYC', 'Estimated Start Date', 'Actual Start Date', 'Actual Completion Date', 'Interim Spending Deadline', '% of Funds to be Spent by Interim Spending Deadine', 'Final Spending Deadline', 'Contract Name', 'Contract Method', 'Contract Status', 'Contract ID #', 'Vendor Name', 'Conttract Start Date', 'Contract End Date', 'New or Existing Contract', 'Revised Contract Start Date', 'Revised Contract End Date', 'Contract Value', 'Payment Recipient', 'Payment Type', 'Payment Date', 'Payment Description', 'Payment Id', 'Payment Value']
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
        out_put_dict = dict()
        head_count = 0
        for element in head:
            out_put_dict[head_count] = element
            head_count += 1
        with open("./csv_head","w") as out_head:
            json.dump(out_put_dict,out_head,indent = 4)

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
                int_key = int(key)
                if debug:
                    print int_key
                    print raw_row[int_key]
                if isinstance(interest_columns_dict[key],list):
                    if raw_row[interest_columns_dict[key][1]] != '' and raw_row[interest_columns_dict[key][2]] != '': 
                        #print raw_row[1]
                        #print raw_row[2]
                        delta_days=int((datetime.strptime(raw_row[interest_columns_dict[key][2]],"%m/%d/%Y %H:%M:%S") - datetime.strptime(raw_row[interest_columns_dict[key][1]],"%m/%d/%Y %H:%M:%S")).days)
                        if debug:
                            print delta_days
                        prefix = interest_columns_dict[key][0]
                        if delta_days <= 1:
                            processed_row.append(prefix+':less than 1 day')
                        elif delta_days <=5:
                            processed_row.append(prefix+':less than 5 day')
                        elif delta_days <=10:
                            processed_row.append(prefix+':less than 10 day')
                        elif delta_days <=20:
                            processed_row.append(prefix+':less than 20 day')
                        elif delta_days <=30:
                            processed_row.append(prefix+':less than 1 month')
                        else:
                            processed_row.append(prefix+':more than 1 month')
                        #print time.strptime("%m/%d/%y %H:%M","0"+raw_row[1])
                        #raw_input()
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

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


interest_columns_dict = {
    #"0": "Unique Key", 
    "97": ["Solve Time",1,2], 
    "98": ["Season",1], 
#    "0": "Unique Key", 
#    "1": "Created Date", 
#    "2": "Closed Date", 
    "3": "Agency", 
#    "4": "Agency Name", 
    "5": "Complaint Type", 
#    "6": "Descriptor", 
    "7": "Location Type", 
#    "8": "Incident Zip", 
#    "9": "Incident Address", 
#    "10": "Street Name", 
#    "11": "Cross Street 1", 
#    "12": "Cross Street 2", 
#    "13": "Intersection Street 1", 
#    "14": "Intersection Street 2", 
#    "15": "Address Type", 
#    "16": "City", 
#    "17": "Landmark", 
#    "18": "Facility Type", 
#    "19": "Status", 
#    "20": "Due Date", 
#    "21": "Resolution Action Updated Date", 
#    "22": "Community Board", 
    "23": "Borough", 
#    "24": "X Coordinate (State Plane)", 
#    "25": "Y Coordinate (State Plane)", 
#    "26": "Park Facility Name", 
#    "27": "Park Borough", 
#    "28": "School Name", 
#    "29": "School Number", 
#    "30": "School Region", 
#    "31": "School Code", 
#    "32": "School Phone Number", 
#    "33": "School Address", 
#    "34": "School City", 
#    "35": "School State", 
#    "36": "School Zip", 
#    "37": "School Not Found", 
#    "38": "School or Citywide Complaint", 
#    "39": "Vehicle Type", 
#    "40": "Taxi Company Borough", 
#    "41": "Taxi Pick Up Location", 
#    "42": "Bridge Highway Name", 
#    "43": "Bridge Highway Direction", 
#    "44": "Road Ramp", 
#    "45": "Bridge Highway Segment", 
#    "46": "Garage Lot Name", 
#    "47": "Ferry Direction", 
#    "48": "Ferry Terminal Name", 
#    "49": "Latitude", 
#    "50": "Longitude", 
#    "51": "Location"
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
        raw_input()
        
        for raw_row in raw_transactions:
            if count > max_rows:
                break
            if line%20 == 0:
                processed_row = list()
                flag = True
                for key in interest_columns_dict.keys():
# process date
                    int_key = int(key)
                    if int_key==97:
                        if raw_row[interest_columns_dict[key][1]] != '' and raw_row[interest_columns_dict[key][2]] != '': 
                            #print raw_row[1]
                            #print raw_row[2]
                            delta_days=int((datetime.strptime(raw_row[interest_columns_dict[key][2]],"%m/%d/%Y %I:%M:%S %p") - datetime.strptime(raw_row[interest_columns_dict[key][1]],"%m/%d/%Y %I:%M:%S %p")).days)
                            prefix = interest_columns_dict[key][0]
                            if delta_days <= 0:
                                processed_row.append(prefix+':same day')
                            if delta_days < 7:
                                processed_row.append(prefix+':less than 1 month')
                            elif delta_days >= 30:
                                processed_row.append(prefix+':more than 1 month')
                            elif delta_days >= 7:
                                processed_row.append(prefix+':more than 1 week')
                            #print time.strptime("%m/%d/%y %H:%M","0"+raw_row[1])
                            #raw_input()
                        else:
                            processed_row.append('')
                    elif int_key==98:
                        if raw_row[interest_columns_dict[key][1]] != '' :
                            prefix = interest_columns_dict[key][0]
                            month = datetime.strptime(raw_row[interest_columns_dict[key][1]],"%m/%d/%Y %I:%M:%S %p")
                            month = month.month
                            processed_row.append(prefix+":%s"%(str(month)))
                        else:
                            processed_row.append('')
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

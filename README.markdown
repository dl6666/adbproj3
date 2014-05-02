Project 3 for COMS E6111 Advanced Database Systems
-------------------------------------------------------------

##(A) Your name and your partner's name and Columbia UNI

Cheng Liu (cl3173)
Di Lin	(dl2869)

##(B) A list of all the files that you are submitting:

1.Makefile		 (instructions on how to run the code)
2.run.sh 		 (a shell script that runs the application)
3.adbproj3.py    (the main python script for finding association rules)
4.readcsv.py	 (the python script we used to generate our CSV file) [OPTIONAL]
5.INTEGRATED-DATASET.csv (CSV file containing the INTEGRATED-DATASET file)
6.example-run.txt (output file of the interesting sample run)


##(C) A detailed description explaining:

###(1) which NYC Open Data data set(s) you used to generate the INTEGRATED-DATASET file:

"311 Service Requests 2007" dataset (https://data.cityofnewyork.us/Social-Services/311-Service-Requests-for-2007/aiww-p3af).

###(2) what (high-level) procedure you used to map the original NYC Open Data data set(s) into your INTEGRATED-DATASET file

####a. Data Sampling 
The total 311 data sheet is about 1.8 million records, which is a little bit too large. By test, we found that randomly sample the data from 311 data sheet can also keep the original associate rule when the sampling data set is large enough.
Then we decided to take 1/20 data(about 100K records) from the entire data sheet to build our INTEGRATED-DATASET.csv, what's more,to keep the data uniformly distribute with the entire year, we firstly sorted the data by the event created date, this can be done by the graphic user interface provided by the new york website.
After that, by our pre-processing script naming readcsv.py, we take **one** record per **sequential 20 records**.
It turned out to be the fact that the events occurred in each month are nearly of the same amount.

####b. Data Mapping

The original data contains a lot of fields that are not suitable for naive data mining(for example: filed with contiguous value,such as date format)

After checking the original form, we found that **created date** and **close date** can be mapped into one field called**"solve time"** which represents how soon this event is solved. And we separate the time period into 4 slots to fit this field,namely: *"same day"*,*"less than 1 week"*,*"more than 1 week"* and *"more than 1 month"*.

When this field combing with the agency,the borough or complaint type, this can give us the hint about how soon this event will be solved.

What's more, we mapped the created date to a field called **"season"** by taking out its creation month as (1,2,3,4,etc,12),by this field, we want to see the distribution of each event type.

And we keep some other fields which are listed below, also, there are some fields obviously dependent on other fields, to avoid trivial rules as much as possible with naive a-priori algorithm, we just take one of these highly-coupled columns.

Agency
Complaint Type
Location Type
Borough

At last, we add the head of each column to its content, this will solve the potential problem that different columns have the same value.


###(3) what makes your choice of INTEGRATED-DATASET file interesting (in other words, justify your choice of NYC Open Data data set(s))

As we described in the above section, we creatively map two date format fields to **1.event solve time** and **2.event created month**, these two new fields are very interesting.
By these two fields, we can get the knowledge of how soon a certain event was solved, with these associate rules, we can predict how soon the current event will finally be solved.

For example:
A associate rule called:
[complaint type:water system] =====> solve time:same day (Conf:48.88%,Supp:2.17%)
it will tell us that if water system breaks, there is about 50% possibility that this problem will be solved in the same day. That is, if this occurs in your area, you don't need to worry about too much.

What's more:
[borough:staten island] =====> solve time:less than 1 week (Conf:44.98%,Supp:2.06%)
and 
[borough:bronx] =====> solve time:same day (Conf:42.40%,Supp:3.24%)
can give us the information about, if a event occurred in a certain area, how soon we can expect it will be solved.

And with different agent and different area, we can compare their different efficiency.
The more detailed specification you can found in the later part.

###(4) The explanation should be detailed enough to allow us to recreate your INTEGRATED-DATASET file exactly from scratch from the NYC Open Data site.
####(a)
At first you should open the link to the data sheet
####(b)
**Then you should sort the data sheet by the Created Date**
####(c)
Download the dataset
####(d)
run the python script:
python2.7 readcsv.py -i \<YOUR DATA FILE NAME\> -m 100000
(the later -m parameter means that the max records in the output file is 100000(100k))


##(D) clear description of how to run your program

Run the following from the directory where you put run.sh (NOTE: you must cd to that directory before running this command):

sh run.sh \<INTEGRATED-DATASET-FILE\> \<min_sup\> \<min_conf\>

, where:
\<INTEGRATED-DATASET-FILE\> is the path to the CSV file
\<min_sup\> is the value of minimun support
\<min_conf\> is the value of minimun confidence

This will produce a file called output.txt, containing the requisite output for our project.

You can run also run our scripts directly by calling
python2.7 adbproj3.py -i <INTEGRATED-DATASET> -s <min_sup> -m <min_conf> 


##(E) A clear description of the internal design of your project
The source code is within one python script file called adbproj3.py 

###(1) General Design 
Our main design principle is to reduce the data size needed to process. 
**To achieve this goal, we map all the each original string to an unique integer and keeps the mapping as a temporary file in the disk**, obviously, same string will be mapped to the same integer.
In the later *itemsets generation*step and *associate rule generation* step, we don't care what the really value of the integer until we output the rule or the itemset to file. At this step, we will reverse the integer to its real meaning   
For example:
-------------------
pen,ink,diary,soap
pen,ink,diary
pen,diary
pen,ink,soap

will be converted to 
['0', '1', '2', '3'], ['0', '1', '2'], ['0', '2'], ['0', '1', '3']

Then we can store all these records in the memory.

By doing this, we reduce the memory usage and thus operation with this simple number will be faster than tricky string.

And during the converting time, we can also calculate the count of each single item, then store them into a hash table(dict structue in python). this time, we use the *string representation* of the integer as the key(which will be easily expanded to multi-items type)

This step is in the function called
**def processCSV(file_path,debug)**


###(2) Itemsets Generation
By converting the string to integer gives us another benefit that we don't need to sort the list, the itemset list is originally sorted.
For example:
By generating the transferred record list, we know that we have **n** different single items(by checking the largest integer number).
Then we start from 0 to n-1.
By checking the count of the single item with the mini support parameter, we can build L\_1 set, selecting those eligible integer. 
As you can see, because we start from the lowest integer number, and insert the eligible integer one by one, then the itemset L\_1 is sorted originally.
And we will see, during the whole iteration step, every itemsets L\_i is also sorted without any additional operation.

Above step is finished in the function
**genFrequentItemsets**

then genFrequentItemsets will call another sub-function called **genSizeKFrequentItemsets** to calculate itemsets of different length **K**, what's more, we will continue this step until the newly construct itemsets contains no element.

To build a length **K** itemsets L\_k from a length **K-1** itemsets L\_(k-1) which is the core part of the apriori algorithm, we firstly introduce the data structure we use.
For each itemset in the itemsets, the structure is made of of a tuple like:
(['1','5','8'],'1,5,8',set('1','5','8'),'1,5')
The first element in the tuple is the real set of the itemset. 
The second element is a comma separated string, for each different itemset, there will be only one unique string, and we use this string as the key to do the hash-lookup.
The third element is a set structure in python, we can use its "issubset" method to determine whether current set is another records's subset easily.
The last string is used when we combing two strings together, we just need to comparing whether these two strings are equal other than the set. 
For python, every string is treated as a constant, then it will be more efficient.

Along with this L\_(k-1), we also keep the hash count table of each L\_i called H\_i

Actually, these last three structures are used for efficiency, we construct them once and store it with the real set without converting function call everytime which will make the program faster.

To build L\_k, we compare every two pairs of itemset in the L\_(k-1) by order, and we do it by a two level loop from the first element of L\_(k-1), we compare the fourth string of the two itemset tuple, if they are equal we build a temporary length k itemset by simply add the last element of the latter itemset to the first one.

Then we come to the prune step to determine whether every k-1 subset of the temporary itemset is in the previous L\_(k-1) set. 
We can easily check this by checking whether the string key of each k-1 subset is in the hash table H\_i. If so, then this new itemset is eligible in the candidate set.

as we said before, the L\_1 is sorted,then by our two level loop and the way we inserting new element, the L\_2 is also sorted both in the element itself or in the whole set.

By mathematical induction, we can see each L\_i is sorted and each element in L\_i is sorted.

For example:
for L\_1, we have [['1'],['5'],['7']]
then when we are building L\_2, it will be:
\['1'] ['5'] ==> ['1','5']
\['1'] ['7'] ==> ['1','7']
\['5'] ['7'] ==> ['5','7']
then candidates of  L\_2 will be [['1','5'],['1','7'],['5','7']] 

When we have constructed the candidate set of L\_i, we build H\_i with every key with a value 0
for each records, we take every itemset in the candidate set to check whether the itemset is a subset of the record, if it is, we then add it's count in the hash table.

This is just a variant of the **subset** function.
After this,we delete those elements lower than the required support both in L\_i and H\_i.

At last, we keep doing so until the newly generate L\_i becomes a empty set.


###(3) Associate Rule Generation

When we get all the non-empty set L\_i and H\_i, we can easily build the all the associate rule by iterate them.
From the requirement of the project, we know that we need only construct those associate rule with only one item in the RHS(right hand side), then for a certain **K** length itemsets, there should be totally **K** possible associate rules.
For a certain rule, we need only to take out its LHS count in the H\_(i-1) and the total count in the H\_(i), then it just be the associate rule's confidence

This is in the function:
**def genAssociateRule**




##(F) The command line specification of an interesting sample run

-- Run this command to get example-run.txt:

sh run.sh INTEGRATED-DATASET.csv 0.02 0.15

-- Briefly explain why the results are interesting

As mentioned above, since the dataset is so diverse, our support and confidence values have to relatively low in order to get good results. Note, however, that this is by no means outlying information, generated by coincidence. A 5% sample of the 1.88 million rows in this table is still over 100k rows. A support of 2% means that we have about 2k rows that support this rule. The confidence is also explained. Each column's domain has a pretty large range of values.  To accommodate the various values, our confidence has to be sufficiently low. This results directly from the 311 dataset's broad and diverse scope.

As discussed in the sections above, these results are interesting because they have the potential to tell us information we can use to do the prediction in the future.This is real data created by real New Yorkers and tells us information about the various happenings in the city as well as revealing patterns across many dimensions, such as time, location, and government agency. This can help the government manage and allocate its resources efficiently to match the patterns that arise from the raw data.

-------------------------------------------------------------
g) Any additional information that you consider significant

Please refer to the example-run.txt. We have many, many interesting rules
generated. We discuss a few of them here. The ramifications of these rules
are extremely interesting to an analyst and can help the government
restructure its resources in ways that match the data. Please refer to attr_list.txt if
you need clarification on which column the rule is from (which can be easily
inferred).

Here we list some of interesting observations about the rules. We focus on one
fixed value for the LHS in order to simplify the discussion.

1. Complaint Type VS Month

[HEATING] => [January](Conf: 24%, Supp: 3%)
[HEATING] => [December](Conf: 21%, Supp: 3%)
[December] => [HEATING](Conf: 30%, Supp: 3%)
[January] => [HEATING](Conf: 30%, Supp: 3%)
[January,RESIDENTIAL BUILDING] => [HEATING](Conf: 55%, Supp: 3%)

* Observation:
Most complaints about 'HEATING' happen in winter (Dec. and Jan.). This is reasonable because
residents use heating a lot at that time. If there was a contact with 311 in January from a
Residential building, it was highly likely that it was for heating. This can help 311 to devote resources to handling heating problems in January.

2. Agency VS Complaint Type

[HPD] => [HEATING](Conf: 35%, Supp: 13%)
[HPD] => [GENERAL CONSTRUCTION](Conf: 18%, Supp: 7%)
[HPD] => [PLUMBING](Conf: 16%, Supp: 6%)
[HPD] => [NONCONST](Conf: 10%, Supp: 4%)

* Note: HPD = Department of Housing Preservation and Development

* Observation:
Complaints to agency 'HPD' are more about 'HEATING', instead of other types.
'NONCONST' is miscellaneous information such as reported vermin etc.

* Application:
This can be used to make smart workload distribution in each agency.

According to the complaints to Department of Housing Preservation and Development, we know that HPD should have more employees to deal with 'HEATING' problem.

3. Agency VS Borough

[DOT] => [QUEENS](Conf: 30%, Supp: 6%)
[DOT] => [BROOKLYN](Conf: 28%, Supp: 5%)
[DOT] => [MANHATTAN](Conf: 19%, Supp: 4%)
[DOT] => [BRONX](Conf: 13%, Supp: 2%)
[BRONX] => [DOT](Conf: 30%, Supp: 2%)

* Note: DOT = Department of Transportation

* Observation:
Complaints to agency 'DOT' are more likely to happen in 'QUEENS' and 'BROOKLYN'. However,
even though complaints to DOT is the least from the Bronx, a lot of the complaints from
Bronx are to the DOT.

* Application:
This can be used to evaluate the living condition of the borough, especially for the traffic condition in this case.

This either shows that there is much more of transportation issues in Queens and Brooklyn rather than
Manhattan (which is rather counter-intuitive). However, if we consider that Queens and Brooklyn are
residential areas, it makes sense. People are less tolerant of transportation issues in the suburbs.

4. Complaint Type VS Agency VS Borough

[NYPD,BROOKLYN] => [Street/Sidewalk](Conf: 81%, Supp: 2%)
[NYPD,Street/Sidewalk] => [BROOKLYN](Conf: 32%, Supp: 2%)

[DOT,QUEENS] => [Street Light Condition](Conf: 44%, Supp: 2%))
[DOT,Street Light Condition] => [QUEENS](Conf: 33%, Supp: 2%)

[DOB] => [QUEENS](Conf: 34%, Supp: 2%)
[DSNY] => [BROOKLYN](Conf: 33%, Supp: 3%)

* Observation:
The rules list the highest confidence for the borough they are about. Most of the reasons
why the NYPD was called into to Brooklyn was for Street and sidewalk issues. That is, this was
the greatest non-emergency reason for NYPD to go into Brooklyn.  Similarly, for DOT in
Queens due to street light issues. Department of Buildings dealt with Queens while Department
of Sanitation dealt with Brooklyn.

* Application:
This will also help government agencies to make smart workload distribution in each borough.


These are only a few of the rules that were generated. Even with the random
sampling, we have a lot more interesting rules in the example-run.txt file.
With more tweaking of the support and confidence parameters and possibly a
larger sample, we may be able to obtain even more richer results.

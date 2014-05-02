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

##(g) Any additional information that you consider significant.
Following are examples of interesting association rules we found. There are description and use cases following each set of rules. These rules are extremely interesting because they are potientially useful to help agencies and government to distribute their resources wisely and make residents in New York live better. More rules are available in the example-run.txt file. 

###1. Agency VS Borough:
[agency:dot] =====> borough:queens (Conf:30.50%,Supp:5.44%)
[agency:dot] =====> borough:manhattan (Conf:19.43%,Supp:3.47%)
[agency:dot] =====> borough:brooklyn (Conf:30.04%,Supp:5.36%)
[borough:manhattan] =====> agency:nypd (Conf:17.61%,Supp:2.48%)
[borough:manhattan] =====> agency:dot (Conf:24.59%,Supp:3.47%)
[borough:manhattan] =====> agency:dep (Conf:22.54%,Supp:3.18%)
####Description:
Complaints going to Department of Transportation are most likely related to Queens and Brooklyn, and less likely related to manhattan. 
However, complaints related to manhattan are most likely to go to dot. This means although manhattan has the least transportation problems amount these three areas. The transportation problem would still be the area's most severe problem. It is reasonable, because manhattan has so more metro lines running which are old and need to be maintained periodically, and this troubles residents a lot.
####Use cases:
More resources in dot should be allocate to the Queens and Brooklyn branches than the others. But dot in manhattan still should have the most resources among the other departments.

###2. Location type VS Borough:
[location type:street] =====> borough:queens (Conf:28.20%,Supp:2.41%)
[location type:street] =====> borough:manhattan (Conf:25.65%,Supp:2.20%)
[location type:street] =====> borough:brooklyn (Conf:28.72%,Supp:2.46%)
[location type:street/sidewalk] =====> borough:queens (Conf:27.93%,Supp:2.16%)
[location type:street/sidewalk] =====> borough:brooklyn (Conf:31.53%,Supp:2.44%)
####Description:
Street related complaints most likely happen in Queens and Brooklyn. It means there are streets related issues in these areas. Maybe street conditions are not so good in these areas. Or there are not enough parking spots, sidewalks are occupied by lots of cars.
####Use cases:
Government should check out what the real problem is. Measures need to be taken to improve the street conditions to reduce the amount of street related complaits.

###3. Season VS Complaint type:
[complaint type:heating] =====> season:2 (Conf:18.09%,Supp:2.33%)
[complaint type:heating] =====> season:12 (Conf:18.52%,Supp:2.38%)
[complaint type:heating] =====> season:11 (Conf:18.68%,Supp:2.40%)
[complaint type:heating] =====> season:1 (Conf:15.90%,Supp:2.05%)
[season:12] =====> complaint type:heating (Conf:27.65%,Supp:2.38%)
[season:11] =====> complaint type:heating (Conf:27.00%,Supp:2.40%)
[season:1] =====> complaint type:heating (Conf:23.18%,Supp:2.05%)
[season:2] =====> complaint type:heating (Conf:26.19%,Supp:2.33%)
####Description:
Complaints about heating happen mostly during the winter (November to February). It makes sense because winter is likely the only season when heating facilities would be used by habitants. On the other hand, the comlaints agencies get during winter are about heating issues. It makes sense people would stay at home the most of time when it is so cold outside. Issues like street light condition would be less possible to be noticed, let alone complaining about it.
####Use cases:
More attention should be paid on the heating issues during winter. Maybe more human resource should be transferred to the agency that is responsible for the heating problem, e.g. Department of Housing Perservation & Development.

###4. Complaint type VS Solve time
[complaint type:blocked driveway] =====> solve time:same day (Conf:86.21%,Supp:2.65%)
[complaint type:street light condition] =====> solve time:same day (Conf:54.60%,Supp:4.00%)
[complaint type:sewer] =====> solve time:same day (Conf:43.45%,Supp:2.27%)
[complaint type:heating] =====> solve time:more than 1 week (Conf:28.24%,Supp:3.63%)
[complaint type:heating] =====> solve time:less than 1 week (Conf:66.81%,Supp:8.59%)
####Description:
The assosiation rules above tell us what is the likely time range it would be for a specific kind of complaints to be solved. 
In addition, complaints about blocked driveway and street light condition is more likely to be solved the same day, and it is likely to take longer time to solve complaints about sewer and heating issues.
####Use cases:
Residents should be aware of the likely time it would take to solve a specific problem. If it goes beyond the likely time the problem would take to be solved, there maybe something wrong. Residents may consider to contact the agency again to check if the complaint is processed properly.

###5. Borough VS Solve time
[borough:bronx] =====> solve time:same day (Conf:42.40%,Supp:3.24%)
[borough:brooklyn] =====> solve time:same day (Conf:41.80%,Supp:7.73%)
[borough:queens] =====> solve time:same day (Conf:40.68%,Supp:7.69%)
[borough:manhattan] =====> solve time:same day (Conf:33.57%,Supp:4.73%)
####Description:
Complaints are likely to be solved most efficiently in Bronx, and lest efficiently in Manhattan. 
####Use case:
It could be considered as one factor of determinating living condition of residents in specific borough.

###6. Complaint type VS Borough
[complaint type:street light condition] =====> borough:queens (Conf:36.93%,Supp:2.71%)
[complaint type:sewer] =====> borough:queens (Conf:39.97%,Supp:2.09%)
####Description:
Street light problem and sewer problem are most severe in Queens.
####Use cases:
Agencies that are responsible for these kind of problems, e.g. street light problem and sewer problem, should distribute more resources to Queens.

###7. Complaint type VS Agency
[complaint type:water system] =====> agency:dep (Conf:100.00%,Supp:4.45%)
[complaint type:street condition] =====> agency:dot (Conf:100.00%,Supp:4.38%)
[complaint type:sewer] =====> agency:dep (Conf:100.00%,Supp:5.22%)
[complaint type:noise] =====> agency:dep (Conf:100.00%,Supp:2.56%)
[complaint type:noise - street/sidewalk] =====> agency:nypd (Conf:100.00%,Supp:2.12%)
[complaint type:electric] =====> agency:hpd (Conf:100.00%,Supp:2.05%)
[agency:dep] =====> complaint type:water system (Conf:32.25%,Supp:4.45%)
[agency:dep] =====> complaint type:sewer (Conf:37.88%,Supp:5.22%)
[agency:dep] =====> complaint type:noise (Conf:18.57%,Supp:2.56%)
####Description:
We can see the responsibilities of each agency, Department of Environmental protection (dep) is responsible for water system, New York Police Department (NYPD) is responsible for noise - street/sidewalk, and so on.
We can see how the incoming complaints distribute among different agencies. dep gets the most complaints about water system and sewer.
####Use cases:
Residents can use these rules to inquiry corresponding agencies when they encounter specific issues. 
The second observation can help agencies allocate their resources according to the amount of complaints they get about the specific issue. For example, dep should have more human resources dealing with water system and sewer than noise.

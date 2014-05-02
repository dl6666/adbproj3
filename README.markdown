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

After checking the original form, we found that **created date** and **close date** can be mapped into one field called**"solve time"** which represents how soon this event is solved. And we separate the time period into 3 slots to fit this field 


Step 2. Choosing attributes (items)
All the attributes in the 311 are not interesting. Some of them are mostly empty, such as school
information. Some attributes are almost unique for each row, such as latitude and longitude. We
therefore, chose a set of attributes that we focused our attention on. This is the same set included
in our optionally submitted file in data/attr_list.txt, which is used in generate_CSV.py. We parse
our main CSV file and do the sampling and only project on these attributes. One additional change we
did was change the Created Date attribute into a Month (i.e. 01/01/2009 12:00 AM -> January).

Created Date
Agency
Complaint Type
Location Type
Incident Zip
Street Name
Borough

-------------------------------------------------------------
(c) what makes your choice of INTEGRATED-DATASET file interesting (in other words, justify your choice of NYC Open Data data set(s))

This dataset is rich, diverse and massive (one of the largest on the website). As a result, it highly
non-obvious and non-trivial to find out any meaningful patterns and information from this data, which
is where our association rule mining algorithm comes in. Since the dataset is so diverse, it is
possible for us to obtain information about a variety of different issues (among all the  different
types of issues that the 311 calls are about), and cover a lot of ground. Furthermore, 311 routes
and interconnects various departments of the NYC government. We get to see and process this highly
diverse and immensely interconnected data that, not only connects all the different parts of the
city to the government, but also connects all the different parts of the government. We, therefore,
anticipate broad, overarching rules from our data set. However, the caveat is that since the
dataset is so diverse, we need to set our support and confidence values reasonably low to obtain
any sort of interesting results.

-------------------------------------------------------------
d) clear description of how to run your program

Run the following from the directory where you put run.sh (NOTE: you must cd to that directory before running this command):

sh run.sh <INTEGRATED-DATASET-FILE> <min_sup> <min_conf>

, where:
<INTEGRATED-DATASET-FILE> is the path to the CSV file
<min_sup> is the value of minimun support
<min_conf> is the value of minimun confidence

This will produce a file called output.txt, containing the requisite output for our project.

For example, on a CLIC machine:
cd /home/yd2234/ADB/proj3/COMSW6111_P3
sh run.sh data/INTEGRATED-DATASET.csv 0.02 0.1

will produce a file called output.txt in the cwd.

You can run also run our scripts directly by calling
python extract_Rule.py <INTEGRATED-DATASET> <min_sup> <min_conf> <OUTPUT-FILE>

-------------------------------------------------------------
e) A clear description of the internal design of your project

We have only one python script: extract_Rule.py, with two main functions for large itemsets and
association rules respectively.

Part 1. Large Itemsets

This part will extract large itemsets above the given minimum support. The main functions include:
	* extractItemsets: A priori algorithm to extract the large itemsets
	* compute_L1: step 1 for A priori algorithm to compute L_1
	* getCandidate: candidate generation for A Priori Algorithm

Detailed description is as follows:

1. extractItemsets: the main function for A priori algorithm. Here we used the same A priori algorithm as
described in Section 2.1 of the Agrawal and Srikant paper.

Our A priori algorithm is:

	Step 1. Generate large 1-itemsets L_1 by calling function compute_L1.
	Step 2. As long as the previous L_{k-1} is non-empty, we compute the candidate C_k by calling function
            getCandidate. Then keep the candidates whose support is above min-sup as L_k.
	Step 3. Store all the large itemsets {L_k} and return

2. compute_L1: compute the first step of A priori algorithm to get L_1. To avoid reading the input file
multiple times, we also store all the baskets in memory to speed up. After the itemsets have been generated,
we delete this storage to potentially reclaim memory.

3. getCandidate: function to generate the candidates C_k for A priori algorithm. Here we used the similar
Apriori Candidate Generation method as described in Section 2.1.1 of the Agrawal and Srikant paper.

The slight difference is that we will never keep two items from the same column in one basket.
For example, considering the column 'Month', no basket will have two months September and
January. So we changed the join condition as "only the last items in the basket are from different columns".
This is because, unlike the transaction example, our items have different domains (in the transaction, they
were all purchased items). Therefore, it makes no sense to have an itemset like {September, April}. Such
an itemset will not have a non-zero support anyway but we never create such an itemset in the first place.

Our Apriori Candidate Generation method is:

	* Data Structure:
	Each item will contain two fields, the item value and the column number where this item is from. For example,
    one item is ('Bronx',5), which means the value for this item is 'Bronx', and it's from the 5-th column of
    the CSV file, indicating that's the Borough attribute.
	So item.value = 'Bronx', and item.colNo = 5.

	The definitions for L_k and C_k are the same as the paper.

	* Join Step:
	insert into C_k
	select p.item_1, p.item_2, ... , p.item_{k-1}, q.item_{k-1}
	from L_{k-1} p, L_{k-1} q
	where p.item_1 = q.item_1, ..., p.item_{k-2} = q.item_{k-2},
		p.item_{k-1}.colNo < q.item_{k-1}.colNo

	So our the items in each itemset are kept sorted in their column number, instead of lexicographic order. We
    know that in our selected attributes, items in different columns will never be the same (such as 'Month' and
    'Complaint Type' columns will never share values). Therefore, it's ok to define such join condition " only
    the last items in p and q are from different columns".

	* Prune Step:
	Use the same prune method to remove candidates whose subsets are not in L_{k-1} as the paper.


Part 2. Association Rules

Once we have the large itemsets, to get the rules, we simply iterate through our k sized large
itemsets (from k = 2 to the largest one). There are two optimizations we can make.

First is the rule generation itself. The number of rules for all itemsets is very large if we do
it naively and generate all possible rules with >= 1 items in the LHS and =1 items in the RHS
for all k-itemsset. For instance, in a large itemset of size k, the only rules we need to generate
are the rules with k-1 items on the LHS and 1 item on the RHS. This follows because
all rules with < k-1 items on the LHS must have been generated for a smaller k itemset.
For instance, for an itemset {x,y,z}, it must have been created from {x,y} and {x,z}.
It follows that there must be an itemset {y z} also since {x y z} is large. Therefore,
all rules [x] => [z] and [x] => [y] and [y] => [z] must have been generated in a smaller
sized k. This optimization is extremely useful as the number of
rules generated per k-sized itemset is exactly k. Another benefit for this method is that
all rules generated are DISTINCT because the itemsets themselves are distinct (by definition).
As you can see, this optimization is incredibly beneficial and makes the solution elegant.

The second optimization is as discussed in class. We never need to go to the data file
again to calculate the confidence for these rules. Given a rule: [LHS] => [RHS], the
confidence for this rule is Support(LHS U RHS)/Support(LHS). But for a given rule, we
have identified that Support of (LHS U RHS) is the support of the kth-itemset that
generated this rule (because of optimization 1, all k-itemsets only generate k-sized rules).
The Support(LHS) is easily found by looking at the k-1 itemsets and finding the one that
is equal to LHS. In this way, we can calculate the confidence of a rule in near constant time, which
is incredibly useful. We can make this amortized constant by hashing the k-itemsets so that
we can find the support(LHS) in amortized constant time.

Given these optimizations, the functions for generating rules are:
	* extractRules
	* getRules
	* getSupport

1. extractRules
This function starts at itemsets of size 2 and proceeds till the largest size
itemset, generating rules for each itemset using getRules below. It then computes
the confidence for each rules and discards it if it is lower than our minimum
confidence. The support for this rule is exactly the support for the large
itemset. This is also stored in the rule. In other words, a rule is stored in the
format <LHS, RHS, conf, sup>. It stores the rule in a list for later printing.

2. getRules
This function is extremely simple due to our optimization. It simply returns
for each element A in the set, a rule [itemset-A] => [A].

3. getSupport
This function simply finds the itemset that matches the input itemset and retrieves
its stored (from generating large itemsets) support value.

Once both the itemset generation and the rule generation is done, we simply
call our writeFile function that writes out the calculated itemsets and rules
to the output file in the correct format.

-------------------------------------------------------------
f) The command line specification of an interesting sample run

-- Run this command to get example-run.txt:

sh run.sh data/INTEGRATED-DATASET.csv 0.02 0.1

-- Briefly explain why the results are interesting

As mentioned above, since the dataset is so diverse, our support and confidence
values have to relatively low in order to get good results. Note, however, that
this is by no means outlying information, generated by coincidence. A 20% sample
of the 1.7 million rows in this table is still over 340k rows. A support of 2%
means that we have about 7.2k rows that support this rule. The confidence is also
explained. Each column's domain has a pretty large range of values.  To accommodate
the various values, our confidence has to be sufficiently low. This results
directly from the 311 dataset's broad and diverse scope.

As discussed in the sections above, these results are interesting because they
have the potential to tell us information that is diverse and broad in scope. This
is real data created by real New Yorkers and tells us information about the various
happenings in the city as well as revealing patterns across many dimensions, such
as time, location, and government agency. This can help the government manage
and allocate its resources efficiently to match the patterns that arise from the
raw data.

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

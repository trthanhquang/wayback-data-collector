# ================================================================================
# Combines the given software list to the publisher names
# Outputs combinedlist.csv
# ================================================================================

import csv

## remove duplicates in publisherlist.csv
with open('publist.csv', 'rb') as infile, \
     open('processedpublist.csv', 'wb') as outfile:
    seen = set()
    for row in infile:
        ## skip duplicate if publisher_name is already in the set  
        if row.split(',')[1] in seen:
            continue 
        seen.add(row.split(',')[1])
        outfile.write(row)

## match software list to publisher website
pub_list = open('processedpublist.csv', 'rb')
pl = list(pub_list)
sw_list = open('swlist.csv', 'rb')
swl = list(sw_list)

with open('combinedlist.csv', 'wb') as outfile:
    for i in xrange(len(swl)):
       for j in xrange(len(pl)):
           if(swl[i].split(',')[4] == pl[j].split(',')[1]):
               print str(i) + ' ' + swl[i].split(',')[4]
               line = swl[i].split('\r')[0] + ',' + pl[j].split(',')[2]
               outfile.write(line)
               break
    

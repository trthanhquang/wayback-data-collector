# ================================================================================
# Collects the links of the main pages of each publisher every year
# Writes the links into a csv file
# ================================================================================

from bs4 import BeautifulSoup
import urllib2
from itertools import islice 
import csv
import os
import requests

path = './data/'
fieldnames = ['snapshot_date', 'snapshot_time', 'publisher_name', 'url']
urlpart1 = 'http://web.archive.org/web/'
urlpart2 = '1201000000*/'
linkpart1 = 'http://web.archive.org'

count = 478
with open('combinedlist.csv', 'rb') as combinedlist:
    reader = csv.DictReader(combinedlist)
    for row in islice(reader, count, None):
        identifier = row['publisher_name']
        website = row['publisher_site']
        print identifier
        infile = path + identifier + '/' + identifier + '.csv'
        outfile = path + identifier + '/' + identifier + '_links.csv'
        print 'count = ' + str(count)
        count += 1
        if not os.path.exists(infile):
            continue

## Getting info from web.archive.org        
        with open(infile, 'rb') as input, open(outfile, 'wb') as output:
            reader2 = csv.reader(input)
            writer = csv.writer(output)
            writer.writerow(fieldnames)
            for line in reader2:
                year = line[2]
                print year
                url = urlpart1 + year + urlpart2 + website
##                page = urllib2.urlopen(url).read()
                page = requests.get(url).text
                soup = BeautifulSoup(page)
                snapshots = soup.find_all(class_='date tooltip')
                for result in snapshots:
                    date = result.find(class_='day').find('a').get('class')[0]
##                    print year + ', ' + date
                    popup = result.find(class_='pop')
                    for info in popup.find_all('a'):
                        link = info.get('href')
                        link = linkpart1 + link
                        time = info.text
                        outputrow = [date, time, identifier, link]
                        writer.writerow(outputrow)
        print '================================================================================'




    

            
            
        

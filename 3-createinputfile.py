# ================================================================================
# Creates an input file based on publisher name
# Stores into respective dir
# code based on wayback.py
# ================================================================================
from waybackmachine import *
from bs4 import BeautifulSoup as bs
from itertools import islice
import urllib2
import csv

machine = WaybackMachine()
path = './data/'
starturl = 'https://web.archive.org/web/*/'
##useragent = 'Chrome/35.0.1916.114 m'
##useragent = 'Internet Explorer/11.0.9600.17107'

# Check if URL exists in database
def checkURL(url):
    if(machine.hasData(url)):
       return True
    else:
        return False

def getYears(identifier, url):
    urlparser = starturl + url
    page = urllib2.urlopen(urlparser).read()
    soup = bs(page)
    wbMeta = soup.find(id='wbMeta')
##    startyear = input('Start year: ')
##    endyear = input('End year: ')
    if(wbMeta == None):
        startyear = input('Start year: ')
        endyear = input('End year: ')
    else:
        links = wbMeta.find_all('a')
        startyear = int(links[1].text.split(',')[1].split(' ')[1])
        endyear = int(links[2].text.split(',')[1].split(' ')[1])
    return startyear, endyear

# Create input file
## identifier is the publisher name 
def createInputFile(identifier, url):
    toybox = ToyBoxInput()
    print identifier
    print url
    startyear, endyear = getYears(identifier, url)
    toybox.makeInputSeq(identifier, url, startyear, endyear)
    if len(toybox.inputData) > 0:
        filepath = path + identifier + '/' + identifier + '.csv'
        print filepath
        toybox.exportCsv(filepath)
        print 'The input file is created'
    del toybox

count = 1004
with open('combinedlist.csv', 'rb') as infile:
    reader = csv.DictReader(infile)
    for row in islice(reader, count, None):
        identifier = row['publisher_name']
        url = row['publisher_site']
        if (checkURL(url)):
            createInputFile(identifier, url)
        print 'count = ' + str(count)
        count +=1
        print ' ================================================================================'
    

from crawl import *
from database import *
import threading
from itertools import izip

def grouped(iterable, n):
    "s -> (s0,s1,s2,...sn-1), (sn,sn+1,sn+2,...s2n-1), (s2n,s2n+1,s2n+2,...s3n-1), ..."
    return izip(*[iter(iterable)]*n)

def multithread_onYear(itemID):
    year_list = range(2014, 1992, -1)
    for years in grouped(year_list, 4):
        year_threads = []
        for year in years:
            #print year
            t = threading.Thread(target = Crawler(itemID).crawl, args = (year,))
            t.daemon = True
            year_threads.append(t)
        [x.start() for x in year_threads]
        [x.join() for x in year_threads]
    print "%s finished\n" % itemID
    return
    
db = database()
itemID_list = db.getItemID()

for (itemIDs) in grouped(itemID_list,16): #extract 16 IDs at once
    #print itemIDs
    ID_threads = []
    for (itemID,) in itemIDs:
        #print itemID
        t = threading.Thread(target = multithread_onYear, args = (itemID,))
        t.daemon = True
        ID_threads.append(t)
    [x.start() for x in ID_threads]
    [x.join() for x in ID_threads]

from crawl import *
from database import *
import threading

db = database()
itemIDs = db.getItemID()
for itemID in itemIDs:
    threads = []
    for year in range(2014, 1990, -1):
        #print year
        t = threading.Thread(target = Crawler(itemID).crawl, args = (year,))
        threads.append(t)
        t.start()
    [x.join() for x in threads]

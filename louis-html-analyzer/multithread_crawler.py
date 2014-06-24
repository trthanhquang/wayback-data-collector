from stub_crawl import *
from stub_database import *
import threading
from itertools import izip
from Queue import *
from threading import *

def grouped(iterable, n):
    "s -> (s0,s1,s2,...sn-1), (sn,sn+1,sn+2,...s2n-1), (s2n,s2n+1,s2n+2,...s3n-1), ..."
    return izip(*[iter(iterable)]*n)

def worker():
    while True:
        itemID = q.get()
        crawler = Crawler(itemID)
        for year in range(2014, 1995, -1):
            crawler.crawl(year)
        q.task_done()

q = Queue()
for i in range(80):
    t = threading.Thread(target = worker)
    t.daemon = True
    t.start()

itemID_list = database().getItemID(2262, 3392)
for (itemID,) in itemID_list:
    q.put(itemID)
q.join()

import urllib2
from stub_database import *
from selenium import webdriver
from threading import *
from Queue import *

class CrawlEvaluator(object):
    wm = "http://web.archive.org"
    wmstart = "http://web.archive.org/web/"
    
    def __init__ (self, itemID):
        self.itemID = itemID
        self.db = database()
        url = self.db.getWebsiteHomepage(itemID)
        if not url.startswith("http"):
            self.url = "http://" + url
        else:
            self.url = url
        #print self.url
        self.url_list = []
        
    def __getSnapshotLinks (self, year):
        req = urllib2.Request(self.wmstart + str(year) + "0600000000*/" + self.url)
        try:
            page = urllib2.urlopen(req)
            soup = BS(page.read())
            links = soup.findAll("a")
            
            for link in links:
                if re.match("(.*)%s(.*)" % year, str(link), re.I):
                    if not "*" in str(link):
                        linkwm = self.wm + link["href"]
                        self.url_list.append(linkwm)

            self.url_list = sorted(set(self.url_list))
            return self.url_list

        except urllib2.URLError, e:
            #print e
            return []

    def __getExpectedNumberOfLinks (self):
        res = 0
        for year in range (2014, 1995, -1) :
            res += len(self.__getSnapshotLinks(year))
        return res

    def __getActualNumberOfLinks (self):
        return self.db.getNumberOfSnapshots(self.itemID);

    def successfulRate(self):
        actual = self.__getActualNumberOfLinks()
        expected = self.__getExpectedNumberOfLinks()
        if expected == 0 :
            return self.itemID, "No Link to collect"
        return self.itemID, actual, expected, actual*1.0 / expected

def worker():
    while True:
        itemID = q.get()
        print CrawlEvaluator(itemID).successfulRate()
        q.task_done()

q = Queue()
for i in range(10):
    t = Thread(target = worker)
    t.daemon = True
    t.start()

db = database()
itemID_list = db.getItemID(3394, 3610)
for (itemID,) in itemID_list:
    q.put(itemID)

q.join()

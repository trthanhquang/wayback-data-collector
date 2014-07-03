from bs4 import BeautifulSoup as BS
import urllib2
from database import *
from crawlEvaluator import *
from selenium import webdriver
import webbrowser
from threading import *
from Queue import *
import time

q = None

class Crawler(object):
    phantomJSpath = 'C:\phantomjs-1.9.7-windows\phantomjs.exe'
    wm = "http://web.archive.org"
    wmstart = "http://web.archive.org/web/"
    def __init__ (self, itemID):
        global q
        q = Queue()
        self.itemID = itemID
        url = database().getWebsitePriceURL(itemID)
        if url is None or \
           url == "ItemID not found in database" \
           or url == "Free" :
            self.url_list = []
            return
        
        if not url.startswith("http"):
            self.url = "http://" + url
        else:
            self.url = url
            
        for i in range(19):
            t = Thread(target = self.__getSnapshotLinks)
            t.daemon = True
            t.start()
            
        self.url_list = []
        for year in range(2014, 1995, -1):
            q.put(year)
        q.join()
        
        self.url_list = sorted(set(self.url_list), reverse=True)
        #print self.url_list
        
    def __getSnapshotLinks (self):
        year = q.get()
        req = urllib2.Request(self.wmstart + str(year) + "0600000000*/" + self.url)
        try:
            page = urllib2.urlopen(req)
            soup = BS(page.read())
            links = soup.findAll("a")
            for link in links:
                #if re.match("(.*)%s(.*)%s" % (str(year),self.url), str(link), re.I):
                if re.match("(.*)%s(.*)" % year, str(link), re.I):
                    if not "*" in str(link):
                        linkwm = self.wm + link["href"]
                        #### list.append() is thread-safe ####
                        self.url_list.append(linkwm)
            q.task_done()
        except urllib2.URLError, e:
            q.task_done()
            print e

    def __getDataFromPhantomBrowser(self, driver, url):
        driver.get(url)
        data = driver.page_source
        return data

    def __getPhantomJSDriver(self):
        try:
            driver = webdriver.PhantomJS(executable_path=self.phantomJSpath)
            driver.set_page_load_timeout(300)
            return driver
        except Exception as e:
            print "RE-TRYING. Error when getting PhantomBrowser driver: %s" % e
            return None

    def __getDataFromURLLIB(self, link):
        req = urllib2.Request(link)
        try:
            resp = urllib2.urlopen(req)
            return resp.read()
        except Exception as e:
            return "Crawl-error: %s" % e

    def __crawlOne(self):
        driver = None
        while driver is None:
            driver = self.__getPhantomJSDriver()
        
        while True:
            try:
                (index, link) = q.get(True, 2) #2 sec timeout
            except Exception as e:
                ###terminate thread###
                print "Queue empty, all task done. %s" %e
                driver.quit()
                return
            ######################
            date = link[27:35]
            #print date, self.itemID, link
            try:
                #print link
                data = self.__getDataFromPhantomBrowser(driver, link)
                database().storeSnapshot(self.itemID, index, date, link, data)
                q.task_done()
            except Exception as e:
                driver.quit()
                data = self.__getDataFromURLLIB(link)
                if data != "Crawl-error":
                    database().storeSnapshot(self.itemID, index, date, link, data)
                else:
                    print "Crawl-error: %s" % link

                driver = None
                while driver is None:
                    driver = self.__getPhantomJSDriver()
                    
                q.task_done()
                    
    def crawl(self, index_list): #list of indexes of url_list[]
        noThreads = min(self.getNumberOfSnapshots(), 30) + 1
        for i in range(noThreads):
            t = Thread(target = self.__crawlOne)
            t.daemon = True
            t.start()

        for index in index_list:
            if (index < 0 or index >= len(self.url_list)):
                continue
            
            if database().isSnapshotInDB(self.itemID, index) == False:
                q.put((index, self.url_list[index]))

        time.sleep(5) # make sure q.get timeout before join unblocks
        q.join()

    def crawlAll(self):
        self.crawl(list(xrange(self.getNumberOfSnapshots())))

    def getNumberOfSnapshots(self):
        return len(self.url_list)

if __name__ == '__main__':
    itemID_list = database().getItemID(2532, 3392)
    for (itemID,) in itemID_list:
        print itemID, active_count()
        Crawler(itemID).crawlAll()
        crawlEvaluator = CrawlEvaluator(itemID)
        print crawlEvaluator.successfulRate()
        database().storeEvaluation(itemID, crawlEvaluator.successfulRate)
    

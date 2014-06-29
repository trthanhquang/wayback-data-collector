from bs4 import BeautifulSoup as BS
import urllib2
from database import *
from crawlEvaluator import *
from selenium import webdriver
import webbrowser
from threading import *
from Queue import *
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
        '''
        except Exception as e:
            q.task_done()
            q.put(year)
            print "Unhandled Error when collecting links: %s" % e1
        '''
        
    def __getDataFromPhantomBrowser(self, url):
        driver = webdriver.PhantomJS(executable_path=self.phantomJSpath)
        driver.get(url)
        data = driver.page_source
        driver.quit()
        return data

    def __crawlOne(self):
        while True:
            (index, link) = q.get()
            ###terminate thread###
            if (index == -1 and link == ""):
                q.task_done()
                return
            ######################
            date = link[27:35]
            #print date, self.itemID, link
            try:
                data = self.__getDataFromPhantomBrowser(link)    
                database().storeSnapshot(self.itemID, index, date, link, data)
                q.task_done()
            except Exception as e:
                print "RE-CRAWLING. Error when crawling snapshots: %s" % e
                q.task_done()
                q.put((index, link)) #recrawl
            
    def crawl(self, index_list): #list of indexes of url_list[]
        for i in range(100):
            t = Thread(target = self.__crawlOne)
            t.daemon = True
            t.start()

        for index in index_list:
            if (index < 0 or index >= len(self.url_list)):
                continue
            
            if database().isSnapshotInDB(self.itemID, index) == False:
                q.put((index, self.url_list[index]))
        q.join()

        for i in range(active_count() - 1):
            q.put((-1, ""))
        q.join()
            
    def crawlAll(self):
        self.crawl(list(xrange(self.getNumberOfSnapshots())))

    def getNumberOfSnapshots(self):
        return len(self.url_list)

if __name__ == '__main__':
    itemID_list = database().getItemID(2262, 3392)
    for (itemID,) in itemID_list:
        print itemID, active_count()
        Crawler(itemID).crawlAll()
        print CrawlEvaluator(itemID).successfulRate()

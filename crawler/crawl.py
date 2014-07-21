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
        self.url_list = []
        if url is not None and "." in url :    
            if not url.startswith("http"):
                self.price_url = "http://" + url
            else:
                self.price_url = url

            self.url_list.append(self.price_url)
            for i in range(19):
                t = Thread(target = self.__getSnapshotLinks, args = (self.price_url,))
                t.daemon = True
                t.start()
                
            for year in range(2014, 1995, -1):
                q.put(year)
            q.join()

        url = database().getWebsiteFeatureURL(itemID)
        self.sameLink = False
        if url is not None and "." in url:
            if not url.startswith("http"):
                self.feature_url = "http://" + url
            else:
                self.feature_url = url

            if not (url == database().getWebsitePriceURL(itemID)):
                self.url_list.append(self.feature_url)
                for i in range(19):
                    t = Thread(target = self.__getSnapshotLinks, args = (self.feature_url,))
                    t.daemon = True
                    t.start()
                    
                for year in range(2014, 1995, -1):
                    q.put(year)
                q.join()
            else:
                self.sameLink = True
            
        self.url_list = sorted(set(self.url_list), reverse=True)
        
    def __getSnapshotLinks (self, url):
        year = q.get()
        req = urllib2.Request(self.wmstart + str(year) + "0600000000*/" + url)
        try:
            page = urllib2.urlopen(req)
            soup = BS(page.read())
            links = soup.findAll("a")
            for link in links:
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
        try:
            driver.get(url)
            data = driver.page_source
            return data
        except Exception as e:
            print "RE-TRYING. Error when getting data from PhantomBrowser: %s, URL: %s" % (e, url)
            return None


    def __getPhantomJSDriver(self):
        try:
            driver = webdriver.PhantomJS(executable_path=self.phantomJSpath)
            driver.set_page_load_timeout(500)
            return driver
        except Exception as e:
            print "RE-TRYING. Error when getting PhantomBrowser driver: %s" % e
            return None

    def __getPhantomJSDriverWithRetry(self, retry):
        driver = None
        while (driver is None) and (retry > 0):
            retry = retry - 1
            driver = self.__getPhantomJSDriver()
        return driver
    
    def __getDataFromURLLIB(self, link):
        req = urllib2.Request(link)
        try:
            resp = urllib2.urlopen(req)
            return resp.read()
        except Exception as e:
            print "Crawl-error, internet connection? %s" % e
            return None

    def __crawlOne(self):
        driver = self.__getPhantomJSDriverWithRetry(5)
        while True:
            try:
                (index, link) = q.get(True, 2) #2 sec timeout
            except Exception as e:
                print "Queue empty, all task done. %s" %e
                if driver is not None:
                    driver.quit()
                return
            else:
                try:
                    if link.startswith(self.wm):
                        date = link[27:35]
                    else:
                        date = time.strftime("%Y%m%d")
                    data = self.__getDataFromPhantomBrowser(driver, link)
                    if data is None:
                        data = self.__getDataFromURLLIB(link)

                    if data is not None:
                        if self.feature_url in link:
                            database().storeFeatureSnapshot(self.itemID, index, date, link, data)
                        elif self.price_url in link:
                            database().storePriceSnapshot(self.itemID, index, date, link, data)
                        else:
                            print "Price or Feature??? URL: %s. Date: %s" % (link, date)
                    else:
                        print "Crawl-error: %s" % link
                    q.task_done()
                except Exception as e:
                    print e
                    if driver is not None:
                        driver.quit()
                    driver = self.__getPhantomJSDriverWithRetry(5)
                    q.task_done()
                    
    def crawl(self, index_list): #list of indexes of url_list[]
        noThreads = min(self.getNumberOfSnapshots(), 25) + 1
        for i in range(noThreads):
            t = Thread(target = self.__crawlOne)
            t.daemon = True
            t.start()

        for index in index_list:
            if (index < 0 or index >= len(self.url_list)):
                continue
            
            temp_url = self.url_list[index]
            if self.feature_url in temp_url:
                if database().isFeatureSnapshotInDB(self.itemID, index) == False:
                    q.put((index, temp_url))
            elif self.price_url in temp_url:
                if database().isPriceSnapshotInDB(self.itemID, index) == False:
                    q.put((index, temp_url))
    
        time.sleep(5) # make sure q.get timeout before join unblocks
        q.join()
        if self.sameLink:
            database().copyFromFeatureToPrice(self.itemID)

    def crawlAll(self):
        self.crawl(list(xrange(self.getNumberOfSnapshots())))

    def getNumberOfSnapshots(self):
        return len(self.url_list)

if __name__ == '__main__':
    itemID_list = database().getItemID(1, 1130)
    for (itemID,) in itemID_list:
        print itemID, active_count()
        Crawler(itemID).crawlAll()
    

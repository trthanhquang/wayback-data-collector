from bs4 import BeautifulSoup as BS
import urllib2
from database import *
import re
from selenium import webdriver
import webbrowser

class Crawler(object):
    phantomJSpath = 'C:\phantomjs-1.9.7-windows\phantomjs.exe'
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
        print self.url
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
            print e
            return []
        
    def __getDataFromPhantomBrowser(self, url):
        driver = webdriver.PhantomJS(executable_path=self.phantomJSpath)
        driver.get(url)
        data = driver.page_source
        driver.quit()
        return data
    
    def __crawlSnapshot (self, year):
        for link in self.url_list:
            date = link[27:35]
            print date, link
            if self.db.isSnapshotInDB(self.itemID, date):
                print "in DB\n"
                continue
            data = self.__getDataFromPhantomBrowser(link)
            data = re.escape(data)
            self.db.storeSnapshot(self.itemID, date, link, data)

    def crawl(self, year):
        self.__getSnapshotLinks(year)
        self.__crawlSnapshot(year)
            
if __name__ == '__main__':
    crawler = Crawler(3681)
    for year in range (2014, 1979, -1):
        crawler.crawl(year)

    '''db = database()
    f1= open("NewHTML.html", "w")
    tstr = db.retrieveHTML(3395, "20140422")
    
    f1.write(tstr)
    f1.close()

    webbrowser.open("NewHTML.html")
'''
   # threads = []
   # for i in range(20):
   #     t = threading.Thread(target=worker, args=(i,))
   #     threads.append(t)
   #     t.start()

    

import urllib2
import re
import collections
from bs4 import BeautifulSoup as BS
from htmlAnalyzer import *

phantomJSpath = 'C:\phantomjs-1.9.7-windows\phantomjs.exe'
wm = "http://web.archive.org"
wmstart = "http://web.archive.org/web/"

def getSnapshotURL(urlAddr,year):
    if not urlAddr.startswith("http"):
        urlAddr2 = "http://" + urlAddr #if the url does not start with 'http'...
    else:
        urlAddr2 = urlAddr

    req = urllib2.Request(wmstart + str(year) + "0000000000*/" + urlAddr2)
    try:
        page = urllib2.urlopen(req)
        soup = BS(page.read())
        links = soup.findAll("a")

        link_list = []
        for link in links:
            if re.match("(.*)%s(.*)" % year, str(link), re.I):
                if not "*" in str(link):
                    linkwm = wm + link["href"]
                    link_list.append(linkwm)

        url_list = sorted(set(link_list),reverse = True)
        return url_list
    except urllib2.URLError, e:
        print 'exception: ',e
    
if __name__ == '__main__':
    url_list = getSnapshotURL("http://www.bitdefender.com",2013)

    searchString = '''
        Antivirus
        Safe shopping
        Firewall
        Antispam
        Parental Control
        Online Storage
        Facebook guardian
        Device Anti-Theft
        Identity protection
        Tune-Up
    '''
    crawler = htmlCrawler()
    crawler.start()

    for url in url_list:
        date = url[27:35]
        print date,url
        
        html = crawler.crawlHTML(url)
        analyzer = htmlAnalyzer(html)
        print "crawled, analyzing"
        if(analyzer.searchText(searchString)!=-1):
            print "OK"
        else:
            print "Have changes"
            break

    crawler.stop()
  

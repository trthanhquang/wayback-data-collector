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

    req = urllib2.Request(wmstart + str(year) + "0600000000*/" + urlAddr2)
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
    url_list = []
    for year in range(2014,1992,-1):
        url_list.extend(getSnapshotURL("http://www.bitdefender.com/",year))
    print url_list

    searchString = '''
AntivirusSafe shoppingFirewallAntispamParental ControlOnline StorageFacebook
guardianDevice Anti-TheftIdentity protectionTune-Up
    '''
    print len(url_list)
    for url in url_list:
        print url
        
    crawler = phantomCrawler()
    crawler.start()

    hi = len(url_list)
    lo = 0

    while(lo<hi):
        mid = lo+(hi-lo)/2
        url = url_list[mid]
        html = crawler.crawlHTML(url)
        analyzer = htmlAnalyzer(html)
        
        print 'crawled: %s'%(url[27:35])
        if(analyzer.searchText(searchString)==-1):
            hi = mid-1
        else:
            lo = mid+1
        print lo,hi,mid
        
    print mid, url_list[mid][27:35], url_list[mid]
    '''
    for url in url_list:
        date = url[27:35]
        print date,url
        
        html = crawler.crawlHTML(url)
        crawler.extractHTML('a.html')
        
        analyzer = htmlAnalyzer(html)
        #print analyzer.getText()
        
        print "crawled, analyzing"
        if(analyzer.searchText(searchString)!=-1):
            print "OK"
        else:
            print "Have changes"
            break
    '''
    
    crawler.stop()
  

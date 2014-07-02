#Import lib to crawl HTML
from selenium import webdriver
import urllib2
import socket #to catch PhantomJS error
import errno #to catch PhantomJS error

#lib to analyze html
from bs4 import BeautifulSoup as BS
import re #matching algorithm
from snapshotAnalyzer import Snapshot

#lib for multi-threading
from threading import Thread
from Queue import *

#lib to evaluate performance
import time

#lib to save dictionary to file
try:
    import cPickle as pickle
except:
    import pickle

debugMode = True
startTime = time.clock()

phantomJSpath = 'C:\phantomjs-1.9.7-windows\phantomjs.exe'
wm = "http://web.archive.org"
wmstart = "http://web.archive.org/web/"

def urlCrawler(q,url,url_list):
    year = q.get()
    # print 'crawling year %s'%year
    req = urllib2.Request(wmstart + str(year) + "0600000000*/" + url)
    try:
        page = urllib2.urlopen(req)
        soup = BS(page.read())
        links = soup.findAll("a")
        for link in links:
            if re.match("(.*)%s(.*)" % (year), str(link), re.I):
                if not "*" in str(link):
                    linkwm = wm + link["href"]
                    #### list.append() is thread-safe ####
                    url_list.append(linkwm)
                    #print linkwm
        q.task_done()
    except urllib2.URLError, e:
        q.task_done()
        print e

def getURLs(url):
    url_list = []
    yearQueue = Queue()

    for t in range(19):
        t = Thread(target = urlCrawler, args=(yearQueue,url,url_list,))
        t.daemon = True
        t.start()

    for year in range(2014,1995,-1):
        yearQueue.put(year)
    
    yearQueue.join()
    return sorted(set(url_list),reverse = True)

def getPhantomJSDriver():
    try:
        driver = webdriver.PhantomJS(executable_path=phantomJSpath)
        driver.set_page_load_timeout(300)
        return driver
    except Exception as e:
        print "RE-TRYING. Error when getting PhantomBrowser driver: %s" % e
        return None

def htmlCrawler(threadId,urlQueue,snapshotList):
    driver = None
    while driver is None:
        driver = getPhantomJSDriver()

    while True:
        url = urlQueue.get()

        if url == 'stop': #Terminating
            break

        start = None
        if debugMode:
            start = time.clock()
            print '[%s:%s] Crawling date = %s. Queue has %s elements'%(threadId,
                time.clock()-startTime,url[27:35],urlQueue.qsize())
        

        try:
            driver.get(url)
            html = driver.page_source.encode('utf-8').decode('utf-8').lstrip().rstrip()

            if debugMode:
                print '[%s:%s] snapshot date %s is crawled [duration: %s]'%(threadId,
                    time.clock()-startTime,url[27:35],time.clock()-start)
            snapshotList.append(Snapshot(url,html))
            urlQueue.task_done()
        except Exception, e:
            print 'Exception while crawling %s'%e
            driver.quit()
            driver = None
            while driver is None:
                driver = getPhantomJSDriver()

            urlQueue.task_done()
            urlQueue.put(url)

    #----------------------------
    if debugMode:
        print '[%s:%s] Thread is terminated! Remains %s thread running'%(threadId,time.clock()-startTime,urlQueue.qsize())
    driver.quit()
    urlQueue.task_done()
    
def getSnapshots(urlList, num_thread = 20):
    snapshotList = []
    urlQueue = Queue()

    for threadId in range(num_thread):
        t = Thread(target = htmlCrawler, args =(threadId,urlQueue,snapshotList,))
        t.daemon = True
        t.start()

    for i in range(len(urlList)):
    # for i in range(num_thread):#testing
        url = urlList[i]
        # print '[main:%s] %s. %s is put into queue'%(time.clock()-startTime,i,url)
        urlQueue.put(url)

    # print '[main:%s] puting terminating characters to queue'%(time.clock()-startTime)

    for i in range(num_thread):
        urlQueue.put('stop')
    urlQueue.join()
    
    return sorted(snapshotList,reverse=True)

''' EXAMPLES FUNCTIONS '''
def crawl(url,numOfThreads = 30):
    urlList = getURLs(url)
    
    if debugMode:
        print '[main:%s] %s snapshots found'%(time.clock()-startTime,len(urlList))
    else:
        print '%s snapshots found'%(len(urlList))

    crawledData = getSnapshots(urlList,num_thread = numOfThreads)

    # i = 0
    # for snapshot in data:
    #     print i, crawledData
    #     i = i+1

    print 'saving to file'
    pickle.dump(crawledData, open("data.p","wb"))

    data = pickle.load(open("data.p","rb"))

    i = 0
    for snapshot in data:
        print i, snapshot
        i = i+1
    
    
if __name__ == '__main__':
    # url = raw_input('URL: ')
    #url = 'http://www.aone-video.com/avi.htm'
    url = 'http://www.swishzone.com/index.php?area=purchase'
    crawl(url)

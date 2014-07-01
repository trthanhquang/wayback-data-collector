#Import lib to crawl HTML
from selenium import webdriver
import urllib2
import socket #to catch PhantomJS error
import errno #to catch PhantomJS error

#lib to analyze html
from bs4 import BeautifulSoup as BS
import re #matching algorithm
import nltk #convert html to meaningful text
import os #split lines

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

startTime = None

phantomJSpath = 'C:\phantomjs-1.9.7-windows\phantomjs.exe'
wm = "http://web.archive.org"
wmstart = "http://web.archive.org/web/"

class Snapshot(object):
    def __init__(self,url):
        self.url = url
        self.initialized = False

    def __cmp__(self,other):
        return cmp(self.getDate(),other.getDate())

    def __str__(self):
        return "(%s : %s)"%(self.getDate(),self.url)

    def setHTML(self,html):
        self.initialized = True
        self.soup = BS(html)
        text = nltk.clean_html(str(self.soup))
        self.rawText = os.linesep.join([s for s in text.split('\n') if s.strip() !=''])

    def __readabilityCheck(self,word):
        for c in word:
            if not((ord('a')<= ord(c) <= ord('z')) or (ord('0')<= ord(c) <=ord('9'))):
                return False
        return True

    def find(self,searchText):
        if not self.initialized:
            return -1

        noSpaceText = " ".join(e for e in self.rawText.lower() if self.__readabilityCheck(e))
        searchText = " ".join(e for e in searchText.lower() if self.__readabilityCheck(e))
        return noSpaceText.find(lookupText)

    def isInit(self):
        return self.initialized

    def getDate(self):
        return self.url[27:35]

    def getText(self):
        if not self.initialized:
            return ""

        return self.rawText

def urlCrawler(q,url,url_list):
    year = q.get()
    # print 'crawling year %s'%year
    req = urllib2.Request(wmstart + str(year) + "0600000000*/" + url)
    try:
        page = urllib2.urlopen(req)
        soup = BS(page.read())
        links = soup.findAll("a")
        for link in links:
            if re.match("(.*)%s(.*)%s" % (year,url), str(link), re.I):
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

def htmlCrawler(threadId,urlQueue,snapshotList):
    try:
        driver = webdriver.PhantomJS(executable_path=phantomJSpath)
        
        while True:
            url = urlQueue.get()

            if url == 'stop': #Terminating
                break

            start = time.clock()
            print '[%s:%s] Crawling date = %s. Queue has %s elements'%(threadId,time.clock()-startTime,url[27:35],urlQueue.qsize())
            driver.get(url)
            html = driver.page_source
            
            for snapshot in snapshotList:
                if snapshot == Snapshot(url):
                    snapshot.setHTML(html)
                    duration = time.clock()-start
                    print '[%s:%s] snapshot date %s is crawled [duration: %s]'%(threadId,time.clock()-startTime,url[27:35],duration)
                    urlQueue.task_done()
                    break


        #----------------------------
        driver.quit()
        urlQueue.task_done()
        print '[%s:%s] Thread is terminated! Remains %s thread running'%(threadId,time.clock()-startTime,urlQueue.qsize())

    except socket.error as e:
        if e.errno == errno.WSAECONNRESET:
            print '[%s:%s]10054 Exception: %s'%(threadId,time.clock()-startTime,e)
        else:
            print '[%s:%s]Exception: %s'%(threadId,time.clock()-startTime,e)
        urlQueue.task_done()

def getSnapshots(urlList, num_thread = 30):
    snapshotList = []
    urlQueue = Queue()

    for threadId in range(num_thread):
        t = Thread(target = htmlCrawler, args =(threadId,urlQueue,snapshotList,))
        t.daemon = True
        t.start()

    for i in range(len(urlList)):
        url = urlList[i]
        print '[main:%s] %s. %s is put into queue'%(time.clock()-startTime,i,url)
        urlQueue.put(url)

    print '[main:%s] puting terminating characters to queue'%(time.clock()-startTime)

    for i in range(num_thread):
        urlQueue.put('stop')
    urlQueue.join()
    
    return sorted(snapshotList,reverse=True)

def main():
    # url = raw_input('URL: ')
    url = 'http://www.aone-video.com/avi.htm'
    num_thread = 30

    global startTime
    startTime = time.clock()
    
    urlList = getURLs(url)
    
    curTime = time.clock()-startTime
    print '[main:%s] %s snapshots found'%(curTime,len(urlList))
    
    snapshotList = []
    urlQueue = Queue()

    for i in range(len(urlList)):
        url = urlList[i]
        # print '[main:%s] %s. %s is put into queue'%(time.clock()-startTime,i,url)
        snapshotList.append(Snapshot(url))
        urlQueue.put(url)

    for threadId in range(num_thread):
        t = Thread(target = htmlCrawler, args =(threadId,urlQueue,snapshotList,))
        t.daemon = True
        t.start()

    # print '[main:%s] puting terminating characters to queue'%(time.clock()-startTime)

    for i in range(num_thread):
        urlQueue.put('stop')


    for i in range(len(snapshotList)):
        while not snapshotList[i].isInit():
            continue
            # time.sleep(0.1)
        print 'snapshot %s is initialized'%i

    urlQueue.join()


    # crawledData = getSnapshots(urlList)

    # print 'saving to file'
    # pickle.dump(crawledData, open("data.p","wb"))

    # data = pickle.load(open("data.p","rb"))

    # i = 0
    # for snapshot in data:
    #     print i, snapshot
    #     i = i+1
    
if __name__ == '__main__':
    main()

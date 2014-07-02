from multithreadCrawler import *
from snapshotAnalyzer import *

crawlModeActivated = False

if __name__ == '__main__':
    # url = raw_input('URL: ')
    snapshotList = []
    if crawlModeActivated:
        url = 'http://www.aone-video.com/avi.htm'
        urlList = getURLs(url)
        snapshotList = getSnapshots(urlList,num_thread = 30)
        print "Data Crawling is done! Analyzing now..."
    else:
        snapshotList = pickle.load(open("data.p","rb"))

    snapshotList[0].openHTML()
    keyword = str(raw_input('Enter search keyword: '))

    listLength = len(snapshotList)
    for i in range(listLength):
        snapshot = snapshotList[i]
        print '%s/%s. Analyzing %s'%(i,listLength,snapshot.getDate())
        
        if snapshot.contain(keyword):
            print 'OK'
        elif snapshot.contain("Got an HTTP 302 response at crawl time"):
            print 'Error 302! Continue'
        else:
            #Find new keyword
            print 'Unable to find: '+keyword
            print 'Suspect changes in content!'

            if i>0:
                snapshotList[i-1].compareHTML(snapshotList[i])
            else:
                snapshotList[0].openHTML()

            newKeyword = str(raw_input('Enter new search keyword: '))
            

            #enforce user to key in correct keyword
            while (not snapshot.contain(newKeyword)) and (newKeyword!='-1'):
                print 'Unable to find: '+newKeyword
                newKeyword = str(raw_input('Enter new search keyword: '))

            if newKeyword == '-1':
                print 'Page Error! Skip current snapshot (on day %s) and continue comparing'%snapshot.getDate()
            else:
                print 'Search keyword is changed to: %s'%newKeyword
                keyword = newKeyword 

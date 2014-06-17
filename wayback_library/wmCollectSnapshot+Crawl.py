import urllib2
from BeautifulSoup import BeautifulSoup
import re
import collections
import nltk
import re,os
from selenium import webdriver
import MySQLdb
import urllib
from bs4 import BeautifulSoup as BS
from BeautifulSoup import BeautifulSoup
from wm2 import WaybackMachine as WB
from collections import OrderedDict
import threading

def worker(num):
    phantomJSpath = 'C:\phantomjs-1.9.7-windows\phantomjs.exe'
    db = MySQLdb.connect(host = "localhost", user = "root", passwd = "", db = "wbm")
    db.autocommit(True)
    cur = db.cursor()
    
    wm = "http://web.archive.org"
    wmstart = "http://web.archive.org/web/"
    #urlAddr = "www.netscantools.com"
    #urlAddr = "seriousbit.com"

    lowBound = num * 30
    upBound = (num+1) * 30 - 1
    cur.execute("select `itemID`, `website` from item order by itemID ASC limit %s, %s;"  % (lowBound, upBound));
    rows = cur.fetchall()
    for row in rows:
        itemId = row[0]
        urlAddr = row[1]
        status_query = "select status from status where itemID = %s" % itemId
        cur.execute(status_query)
        status = cur.fetchone()
        if status is not None and status[0] == "DONE":
            print "This product has been processed\n"
            continue
        print "Thread %s\t%s: %s\n" % (num, itemId, urlAddr)
        if not urlAddr.startswith("http"):
            urlAddr2 = "http://" + urlAddr #if the url does not start with 'http'...
        else:
            urlAddr2 = urlAddr

        for year in range (2014, 1979, -1):
            #print wmstart + str(year) + "0000000000*/" + urlAddr2
            req = urllib2.Request(wmstart + str(year) + "0000000000*/" + urlAddr2)
            try:
                page = urllib2.urlopen(req)
            except urllib2.URLError, e:
                continue
                #print e
            #page = urllib2.urlopen(wmstart + str(year) + "0000000000*/" + urlAddr2)
            soup = BeautifulSoup(page.read())
            links = soup.findAll("a")

            link_list = []
            for link in links:
                if re.match("(.*)%s(.*)" % year, str(link), re.I):
                    if not "*" in str(link):
                        linkwm = wm + link["href"]
                        link_list.append(linkwm)

            for final_link in list(set(link_list)):
                date = final_link[27:35].encode('utf8')
                print ("\t%s\t%s\n") % (num, final_link)
                driver = webdriver.PhantomJS(executable_path=phantomJSpath)
                driver.get(final_link)
                crawl_data = driver.page_source.encode('utf8')
                #crawl_data = os.linesep.join([s for s in crawl_data.split('\n') if s.strip() !=''])
                driver.quit()

                soup = BeautifulSoup(crawl_data)
                text = str(soup)
                #print text
                meaningfulText = nltk.clean_html(text)
                meaningfulText = os.linesep.join([s for s in meaningfulText.split('\n') if s.strip() !=''])

                '''write on MySQL craw_data and meaningful text'''
                
                crawl_data = MySQLdb.escape_string(crawl_data)
                #print crawl_data
                meaningfulText = MySQLdb.escape_string(meaningfulText)
                #print meaningfulText

                query = """insert into snapshot_allyear(itemID, snapshot_date, crawl_data, meaningfulText) values(%s, STR_TO_DATE(\"%s\", \"%%Y%%m%%d\"), \"%s\", \"%s\ on duplicate key update");""" % (itemId, date, crawl_data, meaningfulText)
                #print query
                cur.execute(query)
        confirm_query = "insert into status(itemID, status) values (%s, \"%s\") " % (itemId, "DONE")
        cur.execute(confirm_query)
    cur.close()
    db.close()
    return
    
if __name__ == '__main__':
    threads = []
    for i in range(15):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()

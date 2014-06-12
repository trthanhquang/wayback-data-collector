import collections
import urllib2
import nltk
import re,os
from selenium import webdriver
import MySQLdb
import urllib
from bs4 import BeautifulSoup as BS
from BeautifulSoup import BeautifulSoup
from wm2 import WaybackMachine as WB

phantomJSpath = 'C:\phantomjs-1.9.7-windows\phantomjs.exe'

db = MySQLdb.connect(host = "localhost", user = "root", passwd = "", db = "wbm")
cur = db.cursor()
cur.execute("select `itemID`, `Publisher URL Search` from item order by itemID ASC");
for row in cur.fetchmany(2):

    '''get date and link of waybackmachine and put in link[tag]'''

    itemId = row[0];
    query = row[1];
    year = "2014"

    w= WB()
    (status,links)=w.get_wayback_timetable_links(query,year)

    for tag in links:
        print tag,links[tag]
        date = tag.encode('utf8')
        #print date
        '''from each link wm crawl html by using phantomjs'''

        linkwm = links[tag]
        if linkwm =="":
            print 'empty link!'
            continue
        driver = webdriver.PhantomJS(executable_path=phantomJSpath)
        driver.get(linkwm) 
        driver.quit()

        crawl_data = driver.page_source.encode('utf8')


        '''from craw_data convert to meaningful text'''
        soup = BeautifulSoup(crawl_data)
        text = str(soup)
        meaningfulText = nltk.clean_html(text)
        meaningfulText = os.linesep.join([s for s in meaningfulText.split('\n') if s.strip() !=''])

        '''write on MySQL craw_data and meaningful text'''
        
        crawl_data = MySQLdb.escape_string(crawl_data)
        #print crawl_data
        meaningfulText = MySQLdb.escape_string(meaningfulText)
        #print meaningfulText

        query = """insert into snapshot_2014(itemID, date, crawl_data, meaningfulText) values(%s, STR_TO_DATE(\"%s\", \"%%b-%%e-%%Y\"), \"%s\", \"%s\");""" % (itemId, date, crawl_data, meaningfulText)
        #print query
        cur.execute(query)
        db.commit()
        #f = open('query.txt', 'w')
        #for line in query.split('\n') :
        #    if line.strip() != '' :
        #        f.write(line + str('\n'))
        #f.close()
        #return   
    
   

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
cur.execute("select `itemID`, `Publisher URL Search` from item");

for row in cur.fetchmany(2):

    '''get date and link of waybackmachine and put in link[tag]'''

    itemId = row[0];
    def main() :
        query = row[1];
        year = "2014"

        w= WB()
        (status,links)=w.get_wayback_timetable_links(query,year)
        
        for tag in links:
            print tag,links[tag]
            date = tag.encode('utf32')
            '''from each link wm crawl html by using phantomjs'''
            driver = webdriver.PhantomJS(executable_path=phantomJSpath)
            linkwm = links[tag]
            if linkwm =="":
                print 'empty link!'
                continue
            driver.get(linkwm)
           # driver.get("http://www.netscantools.com")
            crawl_data = driver.page_source.encode('utf8')
            driver.quit()
    

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
    
            query = """insert into snapshot_2014(itemID, date, crawl_data, meaningfulText) values(%s, STR_TO_DATE(\"%s\", \"%%b-%%e-%%Y\"), \"%s\", \"%s\");""" % (itemId, date,crawl_data, meaningfulText)
            #print query
            cur.execute(query)
            db.commit()


    if __name__ == "__main__":
        main()

    
   

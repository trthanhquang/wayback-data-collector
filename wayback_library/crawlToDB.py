from lxml import html
from bs4 import BeautifulSoup as BS
from selenium import webdriver
import MySQLdb

phantomJSpath = 'C:\phantomjs-1.9.7-windows\phantomjs.exe'
link = "http://www.bitdefender.com"

db = MySQLdb.connect(host = "localhost", user = "root", passwd = "", db = "wbm")
cur = db.cursor()
cur.execute("select `itemID`, `SubCat+Publisher URL Search` from item");
            
def main():
    #f = open('pageSource.txt','w')
    driver = webdriver.PhantomJS(executable_path=phantomJSpath)
    for row in cur.fetchall():
        print ("%s / %s\n" % (row[0], row[1]))
        link = row[1]
        if link =="":
            print 'empty link!'
            continue
        driver.get(link)
        crawl_data = driver.page_source.encode('utf8')
        crawl_data = MySQLdb.escape_string(crawl_data)
        query = "insert into snapshot(`itemID`, `date`, `crawl_data`) values (%s, %s, \"%s\");" % (row[0], "DATE(NOW())", crawl_data)
        
        cur.execute(query)
        db.commit()
        #f.write(crawl_data.decode("string-escape"))
    driver.quit()    
    #f.close()
    
if __name__ == "__main__":
    main()

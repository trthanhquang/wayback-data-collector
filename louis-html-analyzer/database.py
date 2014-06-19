import MySQLdb
import webbrowser
from bs4 import BeautifulSoup as BS

class database:
    def __init__(self, hostName="localhost", userName="root", password="", database="wbm"):
        self.db = MySQLdb.connect(host = hostName, user = userName,
                                  passwd = password, db = database)
        self.db.autocommit(True)
        self.cur = self.db.cursor()

    def getHTML(self,itemID):
        getHTML_query = "select snapshot_date, crawl_data, meaningfulText from snapshot_allyear where itemID = %s order by snapshot_date desc" % itemID
        self.cur.execute(getHTML_query)
        return self.cur.fetchall() #return type: (date, html, text)

    def saveHTML(self,itemID,date,fName):
        openHTML_query = "select crawl_data from snapshot_allyear where itemID = %s and snapshot_date = STR_TO_DATE(\"%s\", \"%%Y-%%m-%%d\")" % (itemID, date)
        self.cur.execute(openHTML_query)
        html = self.cur.fetchone()

        soup = BS(str(html))
        
        f = open(fName,'w')
        f.write(soup.prettify().encode('utf8'))
        f.close()
        
    def openHTML(self,fName):
        webbrowser.open(fName)

        
if __name__ == '__main__':
    db = database()
    htmlist = db.getHTML(3394)

    for (date,html,text) in htmlist:
        print date
        print '------------------------------------------------------------'
    

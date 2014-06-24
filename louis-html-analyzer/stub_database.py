import MySQLdb
import webbrowser
import re
from bs4 import BeautifulSoup as BS

class database(object):
    def __init__(self, hostName="localhost", userName="root", password="", database="wbm"):
        self.db = MySQLdb.connect(host = hostName, user = userName,
                                  passwd = password, db = database,
                                  charset='utf8', use_unicode=True)
        self.db.autocommit(True)
        self.cur = self.db.cursor()

    def _del__(self):
        self.cur.close()
        self.db.close()

    def getHTML(self,itemID):
        getHTML_query = "select snapshot_date, crawl_data from snapshot_revised where itemID = %s order by snapshot_date desc" % itemID
        self.cur.execute(getHTML_query)
        return self.cur.fetchall() #return type: (date, html, text)

    def saveHTML(self,itemID,date,fName):
        openHTML_query = "select crawl_data from snapshot_revised where itemID = %s and snapshot_date = STR_TO_DATE(\"%s\", \"%%Y-%%m-%%d\")" % (itemID, date)
        self.cur.execute(openHTML_query)
        html = self.cur.fetchone()

        soup = BS(str(html))
        
        f = open(fName,'w')
        f.write(soup.prettify().encode('utf8'))
        f.close()
        
    def openHTML(self,fName):
        webbrowser.open(fName)

    def getWebsiteHomepage(self, itemID):
        getHomepage_query = "select Feature_URL from item where itemID = %s" % itemID
        self.cur.execute(getHomepage_query)
        return str(self.cur.fetchone()[0]) #return type: website URL as String

    def getItemID(self, lower, upper):
        query  = "select itemID from item where itemID >= %s and itemID <= %s" % (lower, upper)
        self.cur.execute(query)
        return self.cur.fetchall() #return type: (itemID)
    
    def isSnapshotInDB(self, itemID, date):
        status_query = "select itemID, snapshot_date from snapshot_revised where itemID = %s and snapshot_date = STR_TO_DATE(\"%s\", \"%%Y%%m%%d\")" % (itemID, date)
        self.cur.execute(status_query)
        status = self.cur.fetchone()
        if status is not None:
            return True
        else:
            return False

    def getNumberOfSnapshots(self, itemID):
        query = "select count(snapshot_date) from snapshot_revised where itemID = %s" %itemID
        self.cur.execute(query)
        return self.cur.fetchone()[0] #return type: #snapshots as Int
    
    def storeSnapshot(self, itemID, date, url, data):
        data = re.escape(data)
        query = """insert ignore into snapshot_revised(itemID, snapshot_date, snapshot_url, crawl_data) values(%s, STR_TO_DATE(\"%s\", \"%%Y%%m%%d\"), \"%s\", \"%s\");""" % (itemID, date, url, data)
        self.cur.execute(query)

    def retrieveHTML(self, itemID, date):
        query = "select crawl_data from snapshot_revised where itemID = %s and snapshot_date = STR_TO_DATE(\"%s\", \"%%Y%%m%%d\");" % (itemID, date)
        self.cur.execute(query)
        return str(self.cur.fetchone()[0]) #return type: html as String

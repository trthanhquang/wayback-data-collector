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
    
    def getHTML(self, index):
        getHTML_query = """select snapshot_date, crawl_data
                            from snapshot_revised
                            where url_list_index = %s
                            order by snapshot_date desc""" % index
        self.cur.execute(getHTML_query)
        return self.cur.fetchall() #return type: (date, html)

    def saveHTML(self,index,fName):
        openHTML_query = """select crawl_data from snapshot_revised
                            where url_list_index = %s""" % (itemID)
        self.cur.execute(openHTML_query)
        html = self.cur.fetchone()

        soup = BS(str(html))
        
        f = open(fName,'w')
        f.write(soup.prettify().encode('utf8'))
        f.close()
        
    def openHTML(self,fName):
        webbrowser.open(fName)
    
    def getWebsiteHomepage(self, itemID):
        getHomepage_query = """select Feature_URL
                                from item where itemID = %s""" % itemID
        self.cur.execute(getHomepage_query)
        return str(self.cur.fetchone()[0]) #return type: website URL as String

    def getItemID(self, lower, upper):
        query  = "select itemID from item where itemID >= %s and itemID <= %s" % (lower, upper)
        self.cur.execute(query)
        return self.cur.fetchall() #return type: (itemID)
    
    def isSnapshotInDB(self, index):
        status_query = """select * from snapshot_revised
                            where url_list_index = %s""" % index
        self.cur.execute(status_query)
        status = self.cur.fetchone()
        if status is not None:
            return True
        else:
            return False

    def getCrawledIndexes(self):
        query = "select url_list_index from snapshot_revised"
        self.cur.execute(query)
        return self.cur.fetchall() #return (indexes)

    def getNumberOfSnapshots(self):
        query = "select count(url_list_index) from snapshot_revised"
        self.cur.execute(query)
        return self.cur.fetchone()[0] #return type: #snapshots as Int
    
    def storeSnapshot(self, index, date, url, data):
        data = re.escape(data)
        query = """insert ignore into snapshot_revised
                (url_list_index, snapshot_date, snapshot_url, crawl_data)
                values(%s, STR_TO_DATE(\"%s\", \"%%Y%%m%%d\"), \"%s\", \"%s\");""" % (index, date, url, data)
        self.cur.execute(query)

    def retrieveHTML(self, index):
        query = """select crawl_data from snapshot_revised
                    where url_list_index = %s);""" % index
        self.cur.execute(query)
        return str(self.cur.fetchone()[0]) #return type: html as String

    def deleteSnapshots(self):
        query = "delete from snapshot_revised"
        self.cur.execute(query)

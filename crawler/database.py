import MySQLdb
import webbrowser
import re
from bs4 import BeautifulSoup as BS

class database(object):
    def __init__(self, hostName="localhost", userName="root",
                 password="", database="crawling"):
        self.db = MySQLdb.connect(host = hostName, user = userName,
                                  passwd = password, db = database,
                                  charset='utf8', use_unicode=True)
        self.db.autocommit(True)
        self.cur = self.db.cursor()

    def _del__(self):
        self.cur.close()
        self.db.close()

    def getWebsiteHomepage(self, itemID):
        getHomepage_query = '''select Website from item
                                where itemID = %s''' % itemID
        self.cur.execute(getHomepage_query)
        url = self.cur.fetchone()
        if url is not None:
            return str(url[0])
        else:
            return "ItemID not found in database"

    def getWebsiteFeatureURL(self, itemID):
        query = '''select Feature_URL from item
                                where itemID = %s''' % itemID
        self.cur.execute(query)
        url = self.cur.fetchone()
        if url is not None:
            return str(url[0])
        else:
            return "ItemID not found in database"

    # return URL as String
    def getWebsitePriceURL(self, itemID):
        query = '''select Price_URL from item
                                where itemID = %s''' % itemID
        self.cur.execute(query)
        url = self.cur.fetchone()
        if url is not None:
            if (url[0] <> "Free"):
                return str(url[0])
            else:
                return " " #generate a 404 on WBM
        else:
            return "ItemID not found in database"

    # return list of itemID
    def getItemID(self, lower, upper):
        query  = '''select itemID from item
                    where itemID >= %s and itemID <= %s''' % (lower, upper)
        self.cur.execute(query)
        return self.cur.fetchall()

    # return True if snapshot had been crawled
    def isSnapshotInDB(self, itemID, index):
        status_query = '''select itemID, url_list_index from snapshot
                        where itemID = %s and
                        url_list_index = %s
                        ''' % (itemID, index)
        self.cur.execute(status_query)
        status = self.cur.fetchone()
        if status is not None:
            return True
        else:
            return False
    
    def storeSnapshot(self, itemID, index, date, url, data):
        data = re.escape(data)
        query = """insert ignore into
                snapshot(itemID, url_list_index, snapshot_date,
                            snapshot_url, crawl_data)
                values(%s, %s,
                        STR_TO_DATE(\"%s\", \"%%Y%%m%%d\"), \"%s\", \"%s\");
                """ % (itemID, index, date, url, data)
        try:
            self.cur.execute(query)
        except Exception as e:
            print e

    # return html data as String
    def retrieveHTML(self, itemID, index):
        query = '''select crawl_data from snapshot
                    where itemID = %s and
                    url_list_index = %s;
                    ''' % (itemID, index)
        self.cur.execute(query)
        data = self.cur.fetchone()
        if data is not None:
            return str(data[0]) #html as String
        else:
            return "Data has not been crawled"

    # return itemName as String
    def getItemName(self, itemID):
        query = "select app_name from item where itemID = %s" % itemID
        self.cur.execute(query)
        itemName = self.cur.fetchone()
        if itemName is not None:
            return str(itemName[0])
        else:
            return "ItemID not found in database"

    # return type: numberOfSnapshots as Int
    def getNumberOfSnapshots(self, itemID):
        query = '''select count(url_list_index) from snapshot
                    where itemID = %s ''' % itemID
        self.cur.execute(query)
        numberOfSnapshots = self.cur.fetchone()
        if numberOfSnapshots is not None:
            return int(numberOfSnapshots[0])
        else:
            return 0

if __name__ == '__main__':
    db = database()
    htmlist = db.getHTML(3394)

    for (date,html,text) in htmlist:
        print date
        print '------------------------------------------------------------'
    

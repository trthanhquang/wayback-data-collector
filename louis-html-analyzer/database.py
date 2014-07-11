import MySQLdb
import webbrowser
import re
from bs4 import BeautifulSoup as BS
import unicodedata

class database(object):
    def __init__(self, hostName="localhost", userName="root",
                 password="", database="crawling"):
        self.db = None
        while self.db is None:
            self.db = self.__getConnection(hostName, userName, password, database)
            
        self.db.autocommit(True)
        self.cur = self.db.cursor()
        
    def __del__(self):
        self.cur.close()
        self.db.close()

    def __getConnection(self, hostName, userName, password, database):
        try:
            return MySQLdb.connect(host = hostName, user = userName,
                                      passwd = password, db = database,
                                      charset='utf8', use_unicode=True)
        except Exception as e:
            print "Init DB connection. Error: %s" %e
            return None

    def getWebsiteHomepage(self, itemID):
        getHomepage_query = '''select Website from item
                                where itemID = %s''' % itemID
        try:
            self.cur.execute(getHomepage_query)    
            url = self.cur.fetchone()
            if url is not None:
                if ("." in url[0]):
                    return url[0].encode('utf-8').decode('utf-8').rstrip().lstrip()
                else:
                    return None
            else:
                return "ItemID not found in database"
        except (MySQLdb.OperationalError):
            self.__del__()
            self.__init__()
            return self.getWebsiteHomepage(itemID)
            
    def getWebsiteFeatureURL(self, itemID):
        query = '''select Feature_URL from item
                                where itemID = %s''' % itemID
        try:
            self.cur.execute(query)
            url = self.cur.fetchone()
            if url is not None:
                if ("." in url[0]):
                    return url[0].encode('utf-8').decode('utf-8').rstrip().lstrip()
                else:
                    return None
            else:
                return "ItemID not found in database"
        except (MySQLdb.OperationalError):
            self.__del__()
            self.__init__()
            return self.getWebsiteFeatureURL(itemID)
            
    # return URL as String
    def getWebsitePriceURL(self, itemID):
        query = '''select Price_URL from item
                                where itemID = %s''' % itemID
        try:
            self.cur.execute(query)
            url = self.cur.fetchone()
            if url is not None:
                if ("." in url[0]):
                    return url[0].encode('utf-8').decode('utf-8').rstrip().lstrip()
                elif ("Free" in url[0]):
                    return "Free"
                else:
                    return None
            else:
                return "ItemID not found in database"
        except (MySQLdb.OperationalError):
            self.__del__()
            self.__init__()
            return self.getWebsitePriceURL(itemID)
            
    # return list of itemID
    def getItemID(self, lower, upper):
        query  = '''select itemID from item
                    where itemID >= %s and itemID <= %s''' % (lower, upper)
        try:
            self.cur.execute(query)
            return self.cur.fetchall()
        except (MySQLdb.OperationalError):
            self.__del__()
            self.__init__()
            return self.getItemID(lower, upper)

    # return True if snapshot had been crawled
    def isSnapshotInDB(self, itemID, index):
        status_query = '''select itemID, url_list_index from snapshot
                        where itemID = %s and
                        url_list_index = %s
                        ''' % (itemID, index)
        try:
            self.cur.execute(status_query)
            status = self.cur.fetchone()
            if status is not None:
                return True
            else:
                return False
        except (MySQLdb.OperationalError):
            self.__del__()
            self.__init__()
            return self.isSnapshotInDB(itemID, index)
    
    def storeSnapshot(self, itemID, index, date, url, data):
        try:
            if isinstance(data, str):
                data = re.escape(data).decode('utf-8', 'ignore')
            else:
                data = re.escape(unicodedata.normalize('NFKD', data)).encode('utf-8', 'ignore').decode('utf-8', 'ignore')
        except Exception as e:
            print "Cannot store to database. Snapshot URL: %s. Error: %s" % (url, e)
        else:
            query = """insert ignore into
                    snapshot(itemID, url_list_index, snapshot_date,
                                snapshot_url, crawl_data)
                    values(%s, %s,
                            STR_TO_DATE(\"%s\", \"%%Y%%m%%d\"), \"%s\", \"%s\");
                    """ % (itemID, index, date, url, data)
            try:
                self.cur.execute(query)
            except Exception as e:
                self.__del__()
                self.__init__()
                print '''Storing snapshot itemID = %s: Error (Probably NO url was given?) %s''' % (itemID, e)
            
    # return html data as String
    def retrieveHTML(self, itemID, index):
        query = '''select crawl_data from snapshot
                    where itemID = %s and
                    url_list_index = %s;
                    ''' % (itemID, index)
        try:
            self.cur.execute(query)
            data = self.cur.fetchone()
            if data is not None:
                return str(data[0]) #html as String
            else:
                return "Data has not been crawled"
        except (MySQLdb.OperationalError):
            self.__del__()
            self.__init__()
            return self.retrieveHTML(itemID, index)
        
    # return itemName as String
    def getItemName(self, itemID):
        query = "select app_name from item where itemID = %s" % itemID
        try:
            self.cur.execute(query)
            itemName = self.cur.fetchone()
            if itemName is not None:
                return itemName[0].encode('utf-8').decode('utf-8').rstrip().lstrip()
            else:
                return "ItemID not found in database"
        except (MySQLdb.OperationalError):
            self.__del__()
            self.__init__()
            return self.getItemName(itemID)

    # return type: numberOfSnapshots as Int
    def getNumberOfSnapshots(self, itemID):
        query = '''select count(url_list_index) from snapshot
                    where itemID = %s ''' % itemID
        try:
            self.cur.execute(query)
            numberOfSnapshots = self.cur.fetchone()
            if numberOfSnapshots is not None:
                return int(numberOfSnapshots[0])
            else:
                return 0
        except (MySQLdb.OperationalError):
            self.__del__()
            self.__init__()
            return self.getNumberOfSnapshots(itemID)

    def storeEvaluation(self, itemID, evaluation):
        query = '''insert into status(itemID, evaluation) values(%s, %s)
                    on duplicate key update evaluation = %s;
                    ''' % (int(itemID), float(evaluation), float(evaluation))
        self.cur.execute(query)
        
    # return type: list of (URL as String, HTML_data as String)
    def getDataList(self, itemID):
        query = '''select snapshot_url, crawl_data from snapshot
                    where itemID = %s ''' % itemID
        try:
            self.cur.execute(query)
            return self.cur.fetchall()
        except (MySQLdb.OperationalError):
            self.__del__()
            self.__init__()
            return self.getDataList(itemID)

    def reportPrice(self, itemID, itemName, snapshot_date, price):
        query = '''insert into report_price(itemID, itemName, snapshot_date, price)
                    values (%s, \"%s\", \"%s\", \"%s\")
                    on duplicate key update price = \"%s\"
                    ''' % (itemID, itemName, snapshot_date, price, price)
        self.cur.execute(query)

    def reportFeature(self, itemID, itemName, snapshot_date, feature):
        query = '''insert into report_feature(itemID, itemName, snapshot_date, feature)
                    values (%s, \"%s\", \"%s\", \"%s\")
                    on duplicate key update feature = \"%s\"
                ''' % (itemID, itemName, snapshot_date, feature,feature)
        self.cur.execute(query)

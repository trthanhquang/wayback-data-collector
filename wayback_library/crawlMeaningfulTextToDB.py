import collections
import urllib2
from BeautifulSoup import BeautifulSoup
import nltk
from nltk import FreqDist
import re, os
import MySQLdb

db = MySQLdb.connect(host = "localhost", user = "root", passwd = "", db = "wbm")
cur = db.cursor()
cur.execute("select `itemID`, `crawl_data` from snapshot");
for row in cur.fetchall():
    itemId = row[0];
    rawData = row[1];
    #rawData.decode("string-escape");
    
    soup = BeautifulSoup(rawData)
    text = str(soup)
    meaningfulText = nltk.clean_html(text)
    meaningfulText = os.linesep.join([s for s in meaningfulText.split('\n') if s.strip() !=''])
    meaningfulText = MySQLdb.escape_string(meaningfulText)
    query = "update snapshot set meaningfulText = \"%s\" where itemID = %s" %(meaningfulText, itemId)
    cur.execute(query)
    db.commit()
    

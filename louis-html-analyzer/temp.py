# -*- coding: cp1252 -*-
from htmlAnalyzer import *
from database import *

itemID = 3395
db = database()
searchString = '''
\n \n \n \n \n \n \n \n \n \n \n
\n \n \t\t\t\n \t\t\n

\n
Our products have been rated 5 stars by most of the shareware sites\n on the internet!
\n
\n
We at PB Software, LLC are dedicated to providing professional\n services and software. We are dedicated to the pursuit of quality and best\n price software for all of our customers.  We hope you enjoy our products and thank you for purchasing them. 
'''

rows = db.getHTML(itemID)

for (snapshot_date, html, text) in rows:
    print (snapshot_date)
    analyzer = htmlAnalyzer(html)
    print "crawled, analyzing"
    if(analyzer.searchText(searchString)!=-1):
        print "OK"
    else:
        print "Have changes"
        db.saveHTML(itemID,snapshot_date,"DiffHTML.html")
        db.openHTML("DiffHTML.html")
        break

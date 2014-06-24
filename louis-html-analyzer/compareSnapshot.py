from crawl import *
from database import *
from htmlAnalyzer import *
import webbrowser
import difflib
import os

path = os.getcwd()

def saveHTML(html,fileName = "temp.html"):
    f = open(fileName,'w')
    f.write(html.encode('utf8'))
    f.close()

def openHTML(html,fileName = "temp1.html"):
    text = htmlAnalyzer(html).getText()
    saveTextAsHTML(text,fName='text1.html')
    
    f = open(fileName,'w')
    #f.write('<a href=\"file:///{}\">TEXT1</a><br><br><br>'.format(path+"\\"+'text1.html'))
    f.write(html)
    f.close()

    webbrowser.open(fileName)

def saveTextAsHTML(text,fName="temp.html",title="TEXT"):
    f = open(fName,'w')
    f.write('<html> <head> <title> {} </title> </head> <body>'.format(title))
    f.write('<style> p{line-height:120%;} </style>')
    f.write('<p style=\"white-space: pre;\">')
    text = '<br>'.join([s for s in text.splitlines() if s])
    f.write(text)
    f.write('</p></body></html>')
    f.close()

def compareHTML(html1,html2):  
    text1 = htmlAnalyzer(html1).getText()
    text2 = htmlAnalyzer(html2).getText()

    saveTextAsHTML(text1,'text1.html','TEXT1(PREV)')
    saveTextAsHTML(text2,'text2.html','TEXT2(CURR)')
    saveHTML(html1,'html1.html')
    saveHTML(html2,'html2.html')
    
    d = difflib.HtmlDiff(wrapcolumn=80)
    html_str = d.make_file(text1.split('\n'),text2.split('\n'))
    
    f = open("compare.html","w")
    f.write('<ul>')
    f.write('<li> <a href=\"file:///{}\">TEXT1(PREV)</a> </li>'.format(path+"\\"+'text1.html'))
    f.write('<li> <a href=\"file:///{}\">TEXT2(CURR)</a> </li>'.format(path+"\\"+'text2.html'))
    f.write('<li> <a href=\"file:///{}\">HTML1(PREV)</a> </li>'.format(path+"\\"+'html1.html'))
    f.write('<li> <a href=\"file:///{}\">HTML2(CURR)</a> </li>'.format(path+"\\"+'html2.html'))
    f.write('</ul>')
    
    f.write(html_str)
    f.close()
    
    webbrowser.open('compare.html')
    
if __name__ == '__main__':  
    db = database()

    html_list = []
    appName = None
    itemID = None
    
    while (len(html_list)==0):
        itemID = int(raw_input('Enter itemID: '))
        appName = db.getItemName(itemID)
        html_list = db.getHTML(itemID)
        print 'App Name: \"%s\" contains %s snapshots'%(appName,len(html_list))
        
        
    initSearch = True
    searchString = ""
    (snapshot_date,html0) = html_list[0]
    prevHTML = html0
    openHTML(html0)
    searchString = str(raw_input('Enter search string: '))

    
    for (snapshot_date, html) in html_list:
        currHTML = html
        print snapshot_date
        analyzer = htmlAnalyzer(html)

        if(analyzer.searchText(searchString)==-1):
            if(analyzer.searchText("Got an HTTP 302 response at crawl time")!=-1):
                print 'Error 302! Continue'
                continue
               
            
            print 'Unable to find: '+searchString
            print 'Suspect change in Content!'

            compareHTML(prevHTML,currHTML)
            
            newSearchString = str(raw_input('Enter new search string: '))
            if(newSearchString == '-1'):
                print 'Page Error! Continue'
                continue
            else:
                searchString = newSearchString
            while (analyzer.searchText(searchString) == -1):
                print 'Unable to find: (%s)'%searchString
                searchString = str(raw_input('Enter new search string: '))
            prevHTML = currHTML
        print 'OK'
        

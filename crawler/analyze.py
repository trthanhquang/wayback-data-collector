from database import *
import nltk
import os
import difflib

path = os.getcwd()

class Analyzer:
    def __init__(self,html):
        self.soup = BS(html)
        text = nltk.clean_html(str(self.soup))
        self.rawText = os.linesep.join([s for s in text.split('\n') if s.strip() !=''])
        
    def exportText(self, destinationFile):
        f = open(destinationFile,'w')
        f.write(self.rawText)
        f.close()

    def __readabilityCheck(self,e):
        for char in e:
            if not((ord('a')<= ord(char) <= ord('z')) \
                   or (ord('0')<= ord(char) <=ord('9'))):
                return False
        return True
    
    def searchText(self, lookupText):
        noSpaceText = " ".\
                      join(e for e in self.rawText.lower() if self.__readabilityCheck(e))
        lookupText = " ".\
                     join(e for e in lookupText.lower() if self.__readabilityCheck(e))

        return noSpaceText.find(lookupText)

    def getText(self):
        return self.rawText

def saveHTML(html,fileName = "temp.html"):
    f = open(fileName,'w')
    f.write(html.encode('utf8'))
    f.close()

def openHTML(html,fileName = "temp1.html"):
    text = Analyzer(html).getText()
    saveTextAsHTML(text,fName='text1.html')
    
    f = open(fileName,'w')
    #f.write('<a href=\"file:///{}\">TEXT1</a><br><br><br>'.format(path+"\\"+'text1.html'))
    f.write(html.encode('utf-8'))
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
    text1 = Analyzer(html1).getText()
    text2 = Analyzer(html2).getText()

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
    itemID = 2300
    mlist = db.getDataList(itemID)
    appName = db.getItemName(itemID)
    print 'App Name: \"%s\" contains %s snapshots'%(appName,len(mlist))

    (snapshot_date,html0) = mlist[0]
    prevHTML = html0
    openHTML(html0)
    
    searchString = str(raw_input('Enter search string: '))
    for (snapshot_date, snapshot_data) in mlist:
        analyzer = Analyzer(snapshot_data)
        currHTML = snapshot_data
        if(analyzer.searchText(searchString)==-1):
            print 'Suspect change in Content!'
            compareHTML(prevHTML, currHTML)
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
        
        

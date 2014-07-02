import difflib #get text difference
import webbrowser #open html/website

from bs4 import BeautifulSoup as BS
import os
import nltk

path = os.getcwd()

class Snapshot(object):
    def __init__(self,url,html):
        self.url = url
        self.html = html
        self.initialized = False

    def __cmp__(self,other):
        return cmp(self.getDate(),other.getDate())

    def __str__(self):
        return "(%s : %s)"%(self.getDate(),self.url)

    def __initialize(self):
        self.initialized = True
        self.soup = BS(self.html)
        text = nltk.clean_html(str(self.soup))
        self.rawText = os.linesep.join([s for s in text.split('\n') if s.strip() !=''])

    def __readabilityCheck(self,word):
        for c in word:
            if not((ord('a')<= ord(c) <= ord('z')) or (ord('0')<= ord(c) <=ord('9'))):
                return False
        return True

    def find(self,keyword):
        if not self.initialized:
            self.__initialize()

        noSpaceText = " ".join(e for e in self.rawText.lower() if self.__readabilityCheck(e))
        keyword = " ".join(e for e in keyword.lower() if self.__readabilityCheck(e))
        return noSpaceText.find(keyword)

    def contain(self,keyword):
        if not self.initialized:
            self.__initialize()        
        if self.find(keyword) != -1:
            return True
        else:
            return False

    def getDate(self):
        return self.url[27:35]

    def getText(self):
        if not self.initialized:
            self.__initialize() 
        return self.rawText

    def getURL(self):
        return self.url

    def openHTML(self, mode ='offline'):
        if mode == 'online':
            webbrowser.open(self.url)
        elif mode == 'offline':
            f = open("temp.html","w")
            f.write(self.html.encode('utf-8'))
            f.close
            webbrowser.open("temp.html")

    def compareHTML(self, other, mode = 'offline'):
        text1 = self.getText()
        text2 = other.getText()
    
        saveTextAsHTML(text1,'text1.html','TEXT1(CURRENT)- %s'%self.getDate())
        saveTextAsHTML(text2,'text2.html','TEXT2(OTHER)- %s'%other.getDate())
        saveHTML(self.html,'html1.html')
        saveHTML(other.html,'html2.html')
        
        d = difflib.HtmlDiff(wrapcolumn=80)
        html_str = d.make_file(text1.split('\n'),text2.split('\n'))
        
        f = open("compare.html","w")

        f.write('<ul>')
        
        f.write('<li> <a href=\"file:///{}\">TEXT1 (CURRENT)</a> </li>'.format(path+"\\"+'text1.html'))
        f.write('<li> <a href=\"%s\">HTML1 (CURRENT) - Online </a> </li>'%self.getURL())
        f.write('<li> <a href=\"file:///{}\">HTML1(CURRENT) - Offline </a> </li>'.format(path+"\\"+'html1.html'))
        
        f.write('<br>')

        f.write('<li> <a href=\"file:///{}\">TEXT2 (OTHER)</a> </li>'.format(path+"\\"+'text2.html'))
        f.write('<li> <a href=\"%s\">HTML2 (OTHER) - Online </a> </li>'%other.getURL())
        f.write('<li> <a href=\"file:///{}\">HTML2(OTHER) - Offline </a> </li>'.format(path+"\\"+'html2.html'))

        f.write('</ul>')
        
        f.write(html_str)
        f.close()
        
        webbrowser.open('compare.html')


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

from bs4 import BeautifulSoup as BS
from selenium import webdriver
import urllib2
import nltk
import os

class phantomCrawler:
    phantomJSpath = 'C:\phantomjs-1.9.7-windows\phantomjs.exe'
    def __init__(self):
        pass
    def start(self):
        self.driver = webdriver.PhantomJS(executable_path=self.phantomJSpath)

    def stop(self):
        self.driver.quit()

    def crawlHTML(self,url):
        self.driver.get(url)
        soup = BS(self.driver.page_source)
        self.html = soup.prettify().encode('utf8')
        return self.html
    
    def extractHTML(self, fileName):
        f = open(fileName,'w')
        f.write(self.html)
        f.close()

class urlCrawler:
    def crawlHTML(self,url):
        page = urllib2.urlopen(url)
        '''    soup = BS(page.read())
        self.html = soup.prettify().encode('utf8')
        return self.html
    '''
        return page.read().encode('utf8')
    def extractHTML(self, fileName):
        f = open(fileName,'w')
        f.write(self.html)
        f.close()
        
class htmlAnalyzer:
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
            if not((ord('a')<= ord(e) <= ord('z')) or (ord('0')<= ord(e) <=ord('9'))):
                return False
        return True
    
    def searchText(self, lookupText):
        #remove spaces:
        '''noSpaceText = " ".join(self.rawText.split())
        lookupText = " ".join(lookupText.split())'''
        #split words using not only \n,' ',\t but also punctuations:
        '''noSpaceText = " ".join(e for e in self.rawText.lower() if e.isalnum())
        lookupText = " ".join(e for e in lookupText.lower() if e.isalnum())
        '''
        noSpaceText = " ".join(e for e in self.rawText.lower() if self.__readabilityCheck(e))
        lookupText = " ".join(e for e in lookupText.lower() if self.__readabilityCheck(e))

        return noSpaceText.find(lookupText)

    def getText(self):
        return self.rawText

def urlCrawlerExample():
    crawler = urlCrawler()
    html2013 = crawler.crawlHTML("http://web.archive.org/web/20130420051748/http://www.bitdefender.com/")
    crawler.extractHTML("page2013.html")

    html2014 = crawler.crawlHTML("http://www.bitdefender.com/")
    crawler.extractHTML("page2014.html")

    analyzer2014 = htmlAnalyzer(html2014)       
    searchString = """
    Antivirus
    Parental Control
    Antispam
    Firewall
    ID Theft Protection
    Safe Banking
    Social Network Protection """
    
    if(analyzer2014.searchText(searchString)!=-1):
        print "HTML contain search String"
    else:
        #html does not contain search String --> manually compare!
        text1 = htmlAnalyzer(html2013).getText()
        text2 = htmlAnalyzer(html2014).getText()

        import difflib
        d = difflib.HtmlDiff()
        html_str = d.make_file(text1.split('\n'),text2.split('\n'))
        f = open("compare.html","w")
        f.write(html_str)
        f.close()
        
        import webbrowser
        webbrowser.open("compare.html")
        webbrowser.open("page2013.html")
        webbrowser.open("page2014.html")
    
    
def phantomCrawlerExample():
    crawler = phantomCrawler()
    crawler.start()
    html2013 = crawler.crawlHTML("http://web.archive.org/web/20130420051748/http://www.bitdefender.com/")
    crawler.extractHTML("page2013.html")
    
    html2014 = crawler.crawlHTML("http://www.bitdefender.com/")
    crawler.extractHTML("page2014.html")
    crawler.stop()
    
    
    page2014 = htmlAnalyzer(html2014)       
    searchString = """
    Antivirus
    Parental Control
    Antispam
    Firewall
    ID Theft Protection
    Safe Banking
    Social Network Protection """
    
    if(page2014.searchText(searchString)!=-1):
        print "HTML contain search String"
    else:
        #html does not contain search String --> manually compare!
        text1 = htmlAnalyzer(html2013).getText()
        text2 = htmlAnalyzer(html2014).getText()

        import difflib
        d = difflib.HtmlDiff()
        html_str = d.make_file(text1.split('\n'),text2.split('\n'))
        f = open("compare.html","w")
        f.write(html_str)
        f.close()
        
        import webbrowser
        webbrowser.open("compare.html")
        webbrowser.open("page2013.html")
        webbrowser.open("page2014.html")
        
if __name__ == "__main__":
    #urlCrawlerExample()
    phantomCrawlerExample()

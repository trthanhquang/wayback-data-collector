from bs4 import BeautifulSoup as BS
from selenium import webdriver
import nltk
import os

class htmlCrawler:
    phantomJSpath = 'C:\phantomjs-1.9.7-windows\phantomjs.exe'
    def __init__(self):
        pass
    def start(self):
        self.driver = webdriver.PhantomJS(executable_path=self.phantomJSpath)
    def stop(self):
        self.driver.quit()
    def extractHTML(self, url, fileName):
        self.driver.get(url)
        soup = BS(self.driver.page_source)
        
        f = open(fileName,'w')
        f.write(soup.prettify().encode('utf8'))
        f.close()

class htmlAnalyzer:
    def __init__(self,sourceHTML):
        pageSource = open(sourceHTML,'r')
        soup = BS(pageSource)
        pageSource.close()
    
        text = nltk.clean_html(str(soup))
        self.rawText = os.linesep.join([s for s in text.split('\n') if s.strip() !=''])
    
    def exportText(self, destinationFile):
        f = open(destinationFile,'w')
        f.write(self.rawText)
        f.close()

    def searchText(self, lookupText):
        #remove spaces:
        noSpaceText = " ".join(self.rawText.split())
        lookupText = " ".join(lookupText.split())
        return noSpaceText.find(lookupText)

    def getText(self):
        return self.rawText
    
if __name__ == "__main__":
    '''crawler = htmlCrawler()
    crawler.start()
    crawler.extractHTML("http://web.archive.org/web/20130420051748/http://www.bitdefender.com/","page2013.html")
    crawler.extractHTML("http://www.bitdefender.com/","page2014.html")
    crawler.stop()
    '''
    
    analyzer = htmlAnalyzer("page2014.html")       
    searchString = """
    Antivirus
    Parental Control
    Antispam
    Firewall
    ID Theft Protection
    Safe Banking
    Social Network Protection """
    
    if(analyzer.searchText(searchString)!=-1):
        print "HTML contain search String"
    else:
        #html does not contain search String --> manually compare!
        text1 = htmlAnalyzer("page2013.html").getText()
        text2 = htmlAnalyzer("page2014.html").getText()

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
        
    

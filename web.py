#-------------------------------------------------------------------------------
# Name:        web.py
# Purpose:     Access to Web
#
# Author:      drtagkim
#
# Created:     22-07-2013
# Copyright:   Dr. Taekyung Kim
# Licence:     private use
#-------------------------------------------------------------------------------

import mechanize, urllib2, time, random,sys
from lxml import etree
#from bs4 import BeautifulSoup
import logging #logfile for errors
from threading import Thread
from bs4 import BeautifulSoup as BS

class HtmlParser:

    def __init__(self,politeness = 10,logFileName = "defaultlog.log",proxyDic = None):
        self.innerHtml = ""
        self.politeness = politeness
        self.proxyDic = proxyDic
        #logging.basicConfig(filename=logFileName, level = logging.INFO)

    def readHtmlMechanize(self,urlAddr,timeout=60):
        time.sleep(self.politeness) #sleep before you do something
        catch = 0
        while True:
            try:
                urlStream = mechanize.urlopen(urlAddr,timeout=timeout)
                self.innerHtml = urlStream.read()
                if self.innerHtml != None and len(self.innerHtml) > 0:
                    break
                else:
                    time.sleep(self.politeness + catch)
                    catch += 5

            except:
                print "[connection error]"
                time.sleep(self.politness + catch + random.randint(0,60))
                catch += 5
                if catch > 30:
                    #logging.warning("[failed] "+urlAddr)
                    self.innerHtml = ""
                    break

        return self.innerHtml

    def readHtmlNormal(self,urlAddr,timeout=60, catch_tolerance_seconds = 10):
        time.sleep(self.politeness) #sleep before you do something
        catch = 0
        innerHtml = ""
        while True:
            try:
                page = urllib2.urlopen(urlAddr,timeout=timeout)
                if page.info().type == "text/html":
                    innerHtml = unicode(page.read(),"utf-8")
                else:
                    innerHtml = ""
                break
                page.close()
            except:
                #sys.stdout.write("[connection error] "+str(catch)+" @" + urlAddr +"\n")
                time.sleep(self.politeness + catch + random.randint(0,60))
                catch += 5
                if catch > catch_tolerance_seconds:
                    #logging.warning("[failed] "+urlAddr)
                    innerHtml = ""
                    break

        return innerHtml

    def readHtmlNormal2(self,urlAddr,timeout=60):
        time.sleep(self.politeness) #sleep before you do something
        innerHtml = ""
        while True:
            try:
                page = urllib2.urlopen(urlAddr,timeout=timeout)
            except:
                sys.stdout.write("c")
                break
            if page.info().type != "text/html":
                sys.stdout.write("?")
                break
            try:
                innerHtml = unicode(page.read(),"utf-8")
                page.close()
                sys.stdout.write(".")
            except:
                sys.stdout.write("u")
                break
            break
        return innerHtml

    def readHtmlFirefox(self,urlAddr,timeout=60):
        if self.proxyDic != None:
            proxy = urllib2.ProxyHandler(self.proxyDic)
            opener = urllib2.build_opener(proxy)
            urllib2.install_opener(opener)
        headers = { 'User-Agent' : 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11' }
        req = urllib2.Request(urlAddr, None, headers)
        catch = 0
        time.sleep(self.politeness) #sleep before you do something
        while True:
            try:
                connection = urllib2.urlopen(req,None,timeout=timeout)
                self.innerHtml = unicode(connection.read(),"utf-8")
                connection.close()
                if self.innerHtml != None and len(self.innerHtml) > 0:
                    break
                else:
                    #time.sleep(self.politeness + catch)
                    #catch += 30
                    break
            except Exception as e:
                sys.stdout.write("[connection error] catch = "+str(catch)+" seconds \n")
                sys.stdout.write("Exception: "+e.message+"\n")
                #time.sleep(self.politeness + catch + random.randint(0,60))
                #catch += 30
                #if catch > 120:
                    #logging.warning("[failed] "+urlAddr)
                    #self.innerHtml = ""
                    #break
                break

        return self.innerHtml

    def parseByXpath(self,xpathCode):
        tree = etree.HTML(self.innerHtml)
        return tree.xpath(xpathCode)

    def getAttrText(self,element,tag):
        attr = element.attrib
        return attr[tag]

    def getText(self,element):
        return element.text

class HtmlParserThread(Thread):
    def __init__(self,queue_addr,queue_page,politeness=10):
        Thread.__init__(self)
        self.queue_addr = queue_addr
        self.queue_page = queue_page
        self.politeness = politeness
    def run(self):
        while True:
            try:
                addr = self.queue_addr.get_nowait()
            except:
                break
            parser = HtmlParser(self.politeness)
            html = parser.readHtmlNormal(addr)
            self.queue_page.put(html)
            self.queue_addr.task_done()


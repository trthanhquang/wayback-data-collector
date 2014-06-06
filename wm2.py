'''
Taekyung Kim
Wayback Machine Library
2014.6.6
'''
from web3 import WebReader2
from time import sleep
from sys import stdout
from bs4 import BeautifulSoup as BS
import urllib, re


class WaybackMachine:
    """
|  General purpose
|  >>> from wm2 import WaybackMachine
|  >>> wm = WaybackMachine()
|  >>> wm.does_have_data('http://www.google.com')
|  >>> check,table = wm.get_wayback_timetable_links('http://www.google.com',2014)
|  >>>
    """
    home = "http://web.archive.org" #wayback machine home
    machine = "http://web.archive.org/web/*/" #query part1
    machinePart1 = "http://web.archive.org/web/" #query part2
    machinePart2 = "1201000000*/" #time item
    search_query = "http://web.archive.org/web/query?type=urlquery&url=" #search query
    def __init__(self):
        pass
    def does_have_data(self,query):
        """
|  Check whether the URL(=query) exists
        """
        assert assert_valid_url(query), "Not valid URL"
        url_parser = urllib.urlopen(WaybackMachine.search_query + query)
        if url_parser.info().type != "text/html": # rule out other types
            url_parser.close()
            return False
        else:
            page = url_parser.read()
            soup = BS(page,"html.parser")
            eles = soup.find_all(id="error") #if id attribute is error
            url_parser.close() # stream close (not actually implemented in Python)
            return len(eles) <= 0 #False = Not here
    def assert_valid_url(self,url):
        """
|  Assertion
        """
        if url == None:
            return False
        if not url.lower().startswith('http'):
            return False
        return True
    def get_wayback_timetable_links(self,urlAddr,year,timeout=60):
        """
|  List up target links for investigation
|  Input: URL (like, http://www.google.com), Year (like, 2014), Timeout (option, in second)
|  Output: result flag (True/False), dictionary
|     Dictionary key = time code
|     Dictionary value = reference URL for each snapshot
        """
        if not urlAddr.startswith("http"):
            urlAddr2 = "http://" + urlAddr #if the url does not start with 'http'...
        else:
            urlAddr2 = urlAddr
        urlAddr2 = WaybackMachine.machinePart1 + str(year) + WaybackMachine.machinePart2 + urlAddr2
        wr = WebReader2(timeout = timeout)
        page = wr.read(urlAddr2)
        if page != "no url" and page != "-1" and page != "0":
            self.soup = BS(page,'html.parser')
            year_checked = self.check_year(self.soup,year) #do year check
            if not year_checked: #if faield
                return False, {}
            links = self.soup.find_all(self.filterAnchorMain,href = re.compile(urlAddr)) #get page links recorded in Wayback Machine
            if links != None and len(links) > 0 : #if there are valid links of captured webpages
                time_table = self.extractHrefFromBsResultSet(links) #pass the Beautifulsoup object
                return True, time_table
            else:
                return False, {}
        else:
            return False, {}
    def filterAnchorMain(self,tag):
        """
|  BeautifulSoup filter
        """
        return tag.has_attr('class')
    def check_year(self,soup,year):
        """
|  Check valid year. Sometimes WaybackMachine has wrong info.
        """
        rv = True
        eles = soup.find_all(class_="month") #see the month data
        for ele in eles:
            id_str = ele.attrs['id'] #see ids
            id_str_list = id_str.split('-') #year-month
            if len(id_str_list) > 1: #if valid
                year_comp = id_str_list[0].strip() #get year
                if str(year_comp) != str(year): #if the year part does not match
                    rv = False #set false
                break #once the test is good, stop
        return rv #return
    def extractHrefFromBsResultSet(self,elements):
        """
|  Extract results as a dictionary object
        """
        time_table = {}
        for ele in elements: #key = date, value = address
            time_table[ele.attrs['class'][0]] = WaybackMachine.home + ele.attrs['href']
        return time_table

# END OF PROGRAM ===============================
# -*- coding:utf-8 -*-
# ================================================================================
# Wayback Machine Endpoint Library
# Developed by Tag Kim (Ph D.)
# This program is a data crawler designed to collect webpages in Wayback Machine.
# Visit http://web.archive.org to get more imformation.
#
# To run the program, you need to install drtag.web Python module.
# Send me an email: masan.korea@gmail.com
# All right reseved.
# ================================================================================
# ====== Import Modules ======#

#from web import HtmlParser
#from web import HtmlParserThread

from web3 import WebReader2
from bs4 import BeautifulSoup as BS
from sys import stdout, exit
from Queue import Queue
from threading import Lock, Thread
from multiprocessing import Pool,cpu_count
from time import strptime
from datetime import date
from util_queue import *
import re, pickle, logging, urllib, csv, sqlite3, zlib, hashlib, copy

# ====== Global Object ======#
lock = Lock()
num_of_multicores = 4 # the number of multicores
multiprocessing_batch_size = 200 #batch size of multiprocessing
# ===== Functions ======#
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# to reduce data size, all page sources are compressed
# in the program, I assume the text code is converted to utf-8
def compress_page_source(text):
    return repr(zlib.compress(repr(text)))
# --------------------------------------------------------------------------------
def decompress_page_source(compressed_one):
    return eval(zlib.decompress(eval(compressed_one)))

# ===== General ===== #
# --------------------------------------------------------------------------------
# --<CLASS>-----------------------------------------------------------------------
#
class WaybackMachine:
    """This class checks if archive.org has ever captured a snapshot of a user given
    URL. If such a record exists, it returns true, else it returns false. To use this
    class, first create a WaybackMachine instance, and then call the instance method
    hasData and giving it a URL parameter."""
    home = "http://web.archive.org" #wayback machine home
    machine = "http://web.archive.org/web/*/" #query part1
    machinePart1 = "http://web.archive.org/web/" #query part2
    machinePart2 = "1201000000*/" #time item
    search_query = "http://web.archive.org/web/query?type=urlquery&url=" #search query
# --------------------------------------------------------------------------------
# Check the querying url does exist in Archive ORG databases
    def hasData(self,query):
        url_parser = urllib.urlopen(WaybackMachine.search_query + query)
        if url_parser.info().type != "text/html":
            url_parser.close()
            return False
        else:
            page = url_parser.read()
            soup = BS(page,"html.parser")
            eles = soup.find_all(id="error")
            url_parser.close()
            return len(eles) <= 0 #False = Not here
# --------------------------------------------------------------------------------
# --<CLASS>-----------------------------------------------------------------------
class PageNode:
    def __init__(self):
        self.parent = None
        self.name = ""
        self.dateKey = ""
        self.url = ""
        self.html_source = ""
        self.children = []
# --------------------------------------------------------------------------------
    def has_children(self):
        return len(self.children) > 0
# --------------------------------------------------------------------------------
    def has_parent(self):
        if self.parent != None:
            return True
        else:
            return False
# --------------------------------------------------------------------------------
# --<CLASS>-----------------------------------------------------------------------
class ToyBoxInput:
    def __init__(self):
        self.inputData = []
    def makeInputSeq(self,identifier,urlAddr,startYear,endYear):
        col1 = [identifier+"_"+str(i) for i in range(startYear, endYear + 1)]
        col2 = [urlAddr for i in range(startYear, endYear + 1)]
        col3 = [i for i in range(startYear, endYear + 1)]
        self.inputData.extend(map(self.helperMakeInputSeq,col1,col2,col3))
# --------------------------------------------------------------------------------
    def helperMakeInputSeq(self,col_item1,col_item2,col_item3):
        return [col_item1,col_item2,col_item3]
# --------------------------------------------------------------------------------
    def exportCsv(self,file_path):
        with open(file_path,'wb') as f:
            csvWriter = csv.writer(f)
            map(csvWriter.writerow,self.inputData)

# ===== Collection Main ===== #
# --------------------------------------------------------------------------------
# --<CLASS>-----------------------------------------------------------------------
class WaybackController:
    def __init__(self,log_file_path):
        self.log_file_path = log_file_path #Log file path
        self.input_items = [] #Input items
        self.setLog() #Logging setup
# --------------------------------------------------------------------------------
    def setLog(self):
        logging.basicConfig(filename = self.log_file_path, level = logging.INFO)
# --------------------------------------------------------------------------------
    def readInputFile(self,input_path): #input file (csv format), (identifier, url, year)
        f = open(input_path)
        reader = csv.reader(f)
        for item in reader:
            self.input_items.append(item) #each item
        f.close()
        logging.info("Input data from "+input_path) #LOG
# --------------------------------------------------------------------------------
    def collectData(self,pickle_jar, num_of_agent = 8):
        logging.info("Start data collection") #LOG
        inputQueue = Queue() #input queue
        for i in self.input_items: #for each item
            inputQueue.put(i)
        for i in range(num_of_agent):
            t = WaybackKit(inputQueue, pickle_jar) #do each line
            t.setDaemon(True) #wait unitl all complete
            t.start() #start the thread
        inputQueue.join() #join the queue

# --------------------------------------------------------------------------------
# --<CLASS>-----------------------------------------------------------------------
class WaybackKit(Thread):
    def __init__(self, inputQueue,pickle_jar):
        Thread.__init__(self)
        self.inputQueue = inputQueue
        if not pickle_jar.endswith("/"): #if the directory does not end with ...
            pickle_jar += "/"
        self.pickle_jar = pickle_jar
# --------------------------------------------------------------------------------
    def run(self):
        while True:
            try:
                (identifier,goThere,year,) = self.inputQueue.get_nowait()
            except:
                break #if the item queue is empty, terminate
            logging.info("Crawling "+identifier +" from @ "+goThere)
            #MAIN CRAWLER AGENT
            crawler = WaybackCrawler(politeness = 10) #Start collect data
            checker = crawler.readWaybackMain(goThere,year) #make a time table
            #if checker is valid, collect the webpage (i.e., main pages),
            #otherwise skip it.
            if checker:
                #check
                pageData = PageData(crawler,identifier) #page data holder, delegation
                pageData.workMain() #do main work
                pageData.orderCheckRedirection() #check redirection
                pageData.workTune() #update the redirection pages
                fname = self.pickle_jar + identifier + ".wayback" #file name (for data storage)
                pageData.constructNodeExportPickle(fname) #export it as a pickle object file
                logging.info("DONE: "+identifier)
                stdout.write("F") #finished
            else:
                stdout.write("N") #no go
            self.inputQueue.task_done() #do next file
# --------------------------------------------------------------------------------
# --<CLASS>-----------------------------------------------------------------------
class WaybackCrawler:
    def __init__(self):
        self.timeTable = dict()
    def readWaybackMain(self,urlAddr,year,timeout=60):
        if not urlAddr.startswith("http"):
            urlAddr2 = "http://" + urlAddr #if the url does not start with 'http'...
        else:
            urlAddr2 = urlAddr
        urlAddr2 = WaybackMachine.machinePart1 + str(year) + WaybackMachine.machinePart2 + urlAddr2
        wr = WebReader2(timeout = timeout)
        page = wr.read(url = urlAddr2, soup = True)
        if page != "no url" and page != "-1" and page != "0":
            self.soup = copy.deepcopy(wr.soup)
            year_checked = self.check_year(self.soup,year) #do year check
            if not year_checked: #if faield
                return False
            links = self.soup.find_all(self.filterAnchorMain,href = re.compile(urlAddr)) #get page links recorded in Wayback Machine
            if links != None and len(links) > 0 : #if there are valid links of captured webpages
                self.extractHrefFromBsResultSet(links) #pass the Beautifulsoup object
            return True
        else:
            return False
#class WaybackCrawler(HtmlParser): #this is a html parser
    #def __init__(self,politeness = 10,logFileName = "",proxyDic = None):
        #HtmlParser.__init__(self,politeness = 10,logFileName = "",proxyDic = None)
        #self.timeTable = dict() #Main time table (it looks like a calendar)
## --------------------------------------------------------------------------------
    #def readWaybackMain(self,urlAddr,year,timeout=60):
        #stdout.write("S") #start
        #if not urlAddr.startswith("http"):
            #urlAddr2 = "http://" + urlAddr #if the url does not start with 'http'...
        #else:
            #urlAddr2 = urlAddr
        ##Wayback Machine query code IMPORTANT!!!
        #urlAddr2 = WaybackMachine.machinePart1 + str(year) + WaybackMachine.machinePart2 + urlAddr2
        #page = self.readHtmlNormal2(urlAddr2,timeout) #The web collector without flexibility
        ##IF page is "" cancel.
        #if len(page) == 0: #if the page is empty
            #return False #go back
        ##-----------YEAR CHECK-----------#
        #self.soup = BS(page,"html.parser") #HTML PARSER OPTION
        #year_checked = self.check_year(self.soup,year) #do year check
        #if not year_checked: #if faield
            #return False
        ##otherwise
        #links = self.soup.find_all(self.filterAnchorMain,href = re.compile(urlAddr)) #get page links recorded in Wayback Machine
        #if links != None and len(links) > 0 : #if there are valid links of captured webpages
            #self.extractHrefFromBsResultSet(links) #pass the Beautifulsoup object
        #return True
# --------------------------------------------------------------------------------
    def filterAnchorMain(self,tag):
        return tag.has_attr('class')
# --------------------------------------------------------------------------------
    def check_year(self,soup,year):
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
# --------------------------------------------------------------------------------
# Although Archieve ORG can show mutliple pages that have the same date, we just only collect one page per day
    def extractHrefFromBsResultSet(self,elements):
        for ele in elements: #key = date, value = address
            self.timeTable[ele.attrs['class'][0]] = WaybackMachine.home + ele.attrs['href']

# --------------------------------------------------------------------------------
# --<CLASS>-----------------------------------------------------------------------
class PageData:
    def __init__(self,waybackCrawler,identifier,number_of_agent = 20):
        self.waybackCrawler = waybackCrawler #master object; pagedata is a delegated one
        self.number_of_agent = number_of_agent #agents
        self.mainPages = dict() #main page
        self.needTuneUrls = dict() #temp, tune
        self.myNode = PageNode() #mypageNode
        self.myNode.name = identifier #identifier (top)
# --------------------------------------------------------------------------------
    def workMain(self):
        inputQueue = Queue() #input queue
        for k,url in self.waybackCrawler.timeTable.items(): #for each day item
            inputQueue.put((k,url,)) #put day, url
        #get output queue
        outputQueue = self.readPages(inputQueue) #delegation function
        while True:
            if outputQueue.empty():
                break
            else:
                (key,page,) = outputQueue.get_nowait() #FIFO, get itme
                self.mainPages[key] = page #allocate, key = day, page = page source
# --------------------------------------------------------------------------------
    def workTune(self):
        inputQueue = Queue()
        for k,url in self.needTuneUrls.items():
            inputQueue.put((k,url,))
            self.waybackCrawler.timeTable[k] = url
        outputQueue = self.readPages(inputQueue)
        while True:
            if outputQueue.empty():
                break
            else:
                (key,page,) = outputQueue.get_nowait()
                self.mainPages[key] = page
# --------------------------------------------------------------------------------
    def orderCheckRedirection(self):
        checker = WaybackRedirectionChecker(self)
        checker.clean()
# --------------------------------------------------------------------------------
    def constructNodeExportPickle(self, pickle_otuput_dir):
        for k,v in self.mainPages.items():
            child = PageNode()
            child.dateKey = k
            child.html_source = compress_page_source(v) #page source compression
            child.url = self.waybackCrawler.timeTable[k]
            child.parent = self.myNode
            self.myNode.children.append(child)
        f = open(pickle_otuput_dir,'wb')
        pickle.dump(self.myNode,f)
        f.close() #close pickle file
        self.clearTempData() #remove old data

    def clearTempData(self):
        self.mainPages.clear()
        self.needTuneUrls.clear()
# --------------------------------------------------------------------------------
    def readPages(self,inputQueue): #get input queue
        outputQueue = Queue() #empty output
        if inputQueue.empty():
            return outputQueue #if no input, return no output
        for _ in range(self.number_of_agent):
            t = WaybackPageCrawler(inputQueue,outputQueue) #execute WaybackPageCrawler
            t.setDaemon(True)
            t.start()
        inputQueue.join()
        return outputQueue

# --------------------------------------------------------------------------------
# --<CLASS>-----------------------------------------------------------------------
class WaybackRedirectionChecker:
    def __init__(self,pageData):
        self.pageData = pageData

    def clean(self):
        for k,v in self.pageData.mainPages.items():
            redireciton_url = self.checkRedirection(v)
            if redireciton_url != None:
                self.pageData.needTuneUrls[k] = WaybackMachine.home + redireciton_url

# --------------------------------------------------------------------------------
    def checkRedirection(self, page):
        soup = BS(page,"html.parser") #HTML PARSER OPTION
        rv = None
        impEles = soup.find_all(class_="impatient")
        if len(impEles) > 0 :
            rv = impEles[0].a['href']
        return rv

# --------------------------------------------------------------------------------
# --<CLASS>-----------------------------------------------------------------------

class WaybackPageCrawler(Thread):
    def __init__(self,queue_addr,queue_page,politeness = 0,timeout = 60,loud=False):
        Thread.__init__(self)
        self.queue_address = queue_addr
        self.queue_page_source = queue_page
        self.timeout = timeout
        self.politeness = politeness
        self.loud = loud
    def terminate(self):
        self.queue_address.put((None,None))    
    def run(self):
        while 1:
            (key, url,) = self.queue_addr.get_nowait() #Tuple
            if url == None:
                self.queue_address.task_done()
                break
            wr = WebReader2(url,timeout = self.timeout,)
            page = wr.read()
            if page != "no url" and page != "-1" and page != "0":
                self.queue_page_source.put_nowait((key,page,))
                if self.loud:
                    sys.stdout.write(":) ")                 
            else:
                self.queue_page_source.put_nowait((key,"error",))
                if self.loud:
                    sys.stdout.write(":( ")                 
            time.sleep(self.politeness)
            self.queue_address.task_done()        

#class WaybackPageCrawler(HtmlParserThread):
    #def __init__(self,queue_addr,queue_page,politeness = 0):
        #HtmlParserThread.__init__(self,queue_addr,queue_page)
## --------------------------------------------------------------------------------
    #def run(self):
        #while True:
            #try:
                #(key, addr,) = self.queue_addr.get_nowait() #Tuple
            #except:
                #break
            #parser = HtmlParser(self.politeness)
            #html = parser.readHtmlNormal2(addr)
            #self.queue_page.put((key,html,))
            #self.queue_addr.task_done()


# ===== Collection Page ===== #
# --------------------------------------------------------------------------------
# --<CLASS>-----------------------------------------------------------------------
class NavigatorController:
    def read_pickle(self,fileName): #read a .wayback data file
        f = open(fileName)
        self.masterNode = pickle.load(f) #set it as a master node (root node)
        f.close()
# --------------------------------------------------------------------------------
    def extract_pages(self):
        cnt = 1 #counter
        total_size = len(self.masterNode.children) #get total page (in a year)
        print ">>> PAGE COLLECTION PROCESSING"
        for child in self.masterNode.children: #for each page (day)
            #explain code meaning
            #?=not html, u=Unicode issue, c=Connection issue, m=Compression issue, .=good"
            print "\nPROGRESS: " + str(cnt) + " / "+ str(total_size)
            page_source = decompress_page_source(child.html_source) #decompress the code
            soup = BS(page_source,"html.parser") #beautiful soup parser
            fingerprint = self.getFingerPrint(child.url)
            tasks = []
            for ele in soup('a'):
                try:
                    addr = ele.attrs['href'].strip()
                    name = ele.text.strip()
                    if addr.find(fingerprint) > 0 and len(name) > 0:
                        nav = Navigator(child,name,addr)
                        nav.start()
                        tasks.append(nav)
                except:
                    continue
            for task in tasks:
                task.join()
            cnt += 1
# --------------------------------------------------------------------------------
    def getFingerPrint(self,url):
        addr = url
        part1 = addr.split("://",2) #http or https; therefore, :// should be enough
        part2 = part1[2].split("/")
        return part2[0]
# --------------------------------------------------------------------------------
    def export_pickle(self,fileName):
        f = open(fileName,'wb')
        pickle.dump(self.masterNode,f)
        f.close()


# --------------------------------------------------------------------------------
# --<CLASS>-----------------------------------------------------------------------
class Navigator(Thread):
    def __init__(self,pageNode,id_name,url):
        Thread.__init__(self)
        self.pageNode = pageNode
        self.id_name = id_name
        self.url = url

    def run(self):
        child = PageNode()
        child.parent = self.pageNode
        child.dateKey = self.pageNode.dateKey
        child.name = self.id_name
        child.url = WaybackMachine.home + self.url
        temp_source = ""
        #check type
        try:
            connection = urllib.urlopen(child.url)
            #check if the page is text/html?
            meta_info = connection.info()
            if meta_info.type != "text/html":
                stdout.write("?")
                connection.close()
                return
        except: #otherwise conneciton error
            temp_source = "CONNECTION ERROR"
            stdout.write("c")
            return
        #read code
        try:
            temp_source = unicode(connection.read(),"utf-8")
            connection.close()
        except:
            stdout.write("u")
            connection.close()
            return
        #compress
        try:
            child.html_source = compress_page_source(temp_source) #ERROR OCCURS
            stdout.write(".")
        except:
            stdout.write("m") #compression error
            return
        lock.acquire()
        self.pageNode.children.append(child)
        lock.release()

# ====== Database ======#
# --------------------------------------------------------------------------------
# --<CLASS>-----------------------------------------------------------------------
class ToyBoxSchema:
    def __init__(self,db_name):
        self.db_name = db_name
        self.connect()
# --------------------------------------------------------------------------------
    def connect(self):
        rv = True
        try:
            self.con = sqlite3.connect(self.db_name)
            self.is_connected = True
        except:
            rv = False
        return rv
# --------------------------------------------------------------------------------
    def create_schema(self):
        sql = "CREATE TABLE IF NOT EXISTS wayback (page_id TEXT,category TEXT,pick_date DATE,url TEXT,element_txt TEXT, page_source TEXT,parent_id TEXT)" #no index now
        cur = self.con.cursor()
        cur.execute(sql)
        self.con.commit()

    def create_analysis_table(self):
        sql = "CREATE TABLE IF NOT EXISTS source_analysis (page_id TEXT, txt_title TEXT, txt_h1 TEXT, txt_h2 TEXT, txt_h3 TEXT, txt_p TEXT, txt_ul TEXT, txt_ol TEXT, txt_a TEXT, txt_address TEXT, txt_pre TEXT)"
        cur = self.con.cursor()
        cur.execute(sql)
        self.con.commit()
# --------------------------------------------------------------------------------
    def disconnect(self):
        self.con.close()
        self.is_connected = False
# --------------------------------------------------------------------------------
    def __del__(self):
        if self.is_connected:
            self.disconnect()

# --------------------------------------------------------------------------------
# --<CLASS>-----------------------------------------------------------------------
class ToyBoxWriteDatabase:
    def __init__(self,db_name):
        self.db_name = db_name
        self.connect()
# --------------------------------------------------------------------------------
    def __del__(self):
        if self.is_connected:
            self.disconnect()
# --------------------------------------------------------------------------------
    def connect(self):
        rv = True
        try:
            self.con = sqlite3.connect(self.db_name)
            self.is_connected = True
        except:
            rv = False
        return rv
# --------------------------------------------------------------------------------
    def update(self):
        sql_1 = "INSERT INTO wayback (page_id, category, pick_date, url, element_txt, page_source,parent_id) VALUES (?,?,?,?,?,?,?);"
        category = self.root_node.name
        print "\nDATABASE UPDATE STARTS"
        cur = self.con.cursor()
        for child1 in self.root_node.children:
            update_data = []
            pick_date = self.trans_dateKey(child1.dateKey)
            url = child1.url
            page_id = self.generate_unique_id(url)
            element_txt = ""
            page_source = child1.html_source
            parent_id = ""
            update_data.append((page_id,category,pick_date,url,element_txt,page_source,parent_id))
            for child2 in child1.children:
                url2 = child2.url
                page_id2 = self.generate_unique_id(url2)
                element_txt2 = child2.name
                page_source2 = child2.html_source
                parent_id2 = page_id
                update_data.append((page_id2,category,pick_date,url2,element_txt2,page_source2,page_id2))
            cur.executemany(sql_1,update_data)
            self.con.commit()
            stdout.write("*")
        print "\nDATABASE UPDATE COMPLETE"


# --------------------------------------------------------------------------------
    def read_pickle(self,pickle_file_path):
        f = open(pickle_file_path)
        self.root_node = pickle.load(f)
        f.close()
        #category = root_node.name
# --------------------------------------------------------------------------------
    def trans_dateKey(self,time_str):
        time_key = "%b-%d-%Y"
        t = strptime(time_str,time_key)
        return date(t.tm_year,t.tm_mon,t.tm_mday)
# --------------------------------------------------------------------------------
    def generate_unique_id(self,url):
        return (hashlib.md5(url)).hexdigest()
# --------------------------------------------------------------------------------
    def disconnect(self):
        self.con.close()
        self.is_connected = False

class ToyBoxWriteDatabase_Analysis:
    def __init__(self,db_name):
        self.db_name = db_name
        self.connect()
# --------------------------------------------------------------------------------
    def __del__(self):
        if self.is_connected:
            self.disconnect()
# --------------------------------------------------------------------------------
    def connect(self):
        rv = True
        try:
            self.con = sqlite3.connect(self.db_name)
            self.is_connected = True
        except:
            rv = False
        return rv
# --------------------------------------------------------------------------------
    def insert_analyze_temp(self,data_set):
        sql_1 = "INSERT INTO source_analysis (page_id,txt_title,txt_h1,txt_h2,txt_h3,txt_p,txt_ul,txt_ol,txt_a,txt_address,txt_pre) VALUES (?,?,?,?,?,?,?,?,?,?,?);"
        cur = self.con.cursor()
        cur.executemany(sql_1,data_set)
        self.con.commit()
        stdout.write("i") #insert

    def disconnect(self):
        self.con.close()
        self.is_connected = False
# --------------------------------------------------------------------------------
# --<CLASS>-----------------------------------------------------------------------
class ToyBoxReadDatabase:
    def __init__(self,db_name):
        self.db_name = db_name
        self.connect()
# --------------------------------------------------------------------------------
    def __del__(self):
        if self.is_connected:
            self.disconnect()
# --------------------------------------------------------------------------------
    def connect(self):
        rv = True
        try:
            self.con = sqlite3.connect(self.db_name)
            self.is_connected = True
        except:
            rv = False
        return rv

    def get_cursor(self):
        return self.con.cursor()

    def disconnect(self):
        self.con.close()
        self.is_connected = False

# ====== Analysis ======#
# --------------------------------------------------------------------------------
# --<CLASS>-----------------------------------------------------------------------
class DictAnalyzePageSource(dict):
    def __init__(self,beautiful_soup_obj):
        self.soup = beautiful_soup_obj
# --------------------------------------------------------------------------------
    def analyze(self):
        self.remove_script()
        self.extract_information()
# --------------------------------------------------------------------------------
    def remove_script(self):
        for s in self.soup("script"): s.extract()
# --------------------------------------------------------------------------------
    def extract_information(self):
        #find those things
        elements_title = self.soup("title")
        elements_p = self.soup("p")
        elements_h1 = self.soup("h1")
        elements_h2 = self.soup("h2")
        elements_h3 = self.soup("h3")
        elements_ul = self.soup("ul")
        elements_ol = self.soup("ol")
        elements_link = self.soup("a")
        elements_address = self.soup("address")
        elements_pre = self.soup("pre")
        #save_data
        self.save_clean_up_to_dict('title',elements_title)
        self.save_clean_up_to_dict('p',elements_p)
        self.save_clean_up_to_dict('h1',elements_h1)
        self.save_clean_up_to_dict('h2',elements_h2)
        self.save_clean_up_to_dict('h3',elements_h3)
        self.save_clean_up_to_dict('ul',elements_ul)
        self.save_clean_up_to_dict('ol',elements_ol)
        self.save_clean_up_to_dict('a',elements_link)
        self.save_clean_up_to_dict('address',elements_address)
        self.save_clean_up_to_dict('pre',elements_pre)
# --------------------------------------------------------------------------------
    def save_clean_up_to_dict(self,key,elements):
        text_value = self.clean_up(elements)
        self[key] = text_value
# --------------------------------------------------------------------------------
    def clean_up(self,elements):
        l1 = [item.text.strip() for item in elements]
        return "\n".join(l1)

class InboxPageReceiver_Multiprocessing:
    def __init__(self,rows_set):
        self.rows_set = rows_set

    def process_function(self,rows):
        result = []
        for row in rows:
            (page_id,page_source,) = row
            page_source = decompress_page_source(page_source) #decompress
            soup = BS(page_source,"html.parser")
            dict_analyzer = DictAnalyzePageSource(soup)
            dict_analyzer.analyze() #analyze the code
            output =(page_id,dict_analyzer['title'],dict_analyzer['h1'],dict_analyzer['h2'],dict_analyzer['h3'],dict_analyzer['p'],dict_analyzer['ul'],dict_analyzer['ol'],dict_analyzer['a'],dict_analyzer['address'],dict_analyzer['pre'])
            stdout.write("a") #analyzing
            result.append(output)
        return result

    def run(self):
        pool = Pool()
        self.result = pool.map(unwrap_inbox_page_receiver,zip([self]*len(self.rows_set),self.rows_set))
        pool.terminate()

def unwrap_inbox_page_receiver(arg,**kwarg):
    return InboxPageReceiver_Multiprocessing.process_function(*arg,**kwarg)

class InboxPageReceiver_SingleProcess:
    def __init__(self,rows):
        self.rows = rows

    def process_function(self,row):
        (page_id,page_source,) = row
        page_source = decompress_page_source(page_source) #decompress

        soup = BS(page_source,"html.parser")
        dict_analyzer = DictAnalyzePageSource(soup)
        dict_analyzer.analyze() #analyze the code
        output =(page_id,dict_analyzer['title'],dict_analyzer['h1'],dict_analyzer['h2'],dict_analyzer['h3'],dict_analyzer['p'],dict_analyzer['ul'],dict_analyzer['ol'],dict_analyzer['a'],dict_analyzer['address'],dict_analyzer['pre'])
        stdout.write("a") #analyzing
        return output

    def run(self):
        self.result = map(self.process_function,self.rows)



class ToyBoxAnalyzeSource_Temp:
    def __init__(self,dbName="d:/999_temp_wayback/wayback.db"):
        self.dbName = dbName
        self.limit = multiprocessing_batch_size
        self.offset = 0
    def go_forward(self):
        self.sql_input = "SELECT page_id,page_source FROM wayback LIMIT %d OFFSET %d;" % (self.limit,self.offset)

    def step_1(self):
        db_schema = ToyBoxSchema(self.dbName)
        db_schema.connect()
        db_schema.create_analysis_table()
        del db_schema

    def step_2(self):
        cnt = 0
        rows_set = []
        while True:
            self.go_forward() #go forward reading point
            db_reader = ToyBoxReadDatabase(self.dbName) #object reader
            db_reader.connect() #connect
            cur = db_reader.get_cursor() #get cursor
            cur.execute(self.sql_input) #get data
            rows = cur.fetchall() #get data
            del db_reader
            if len(rows) <= 0 and len(rows_set) <=0 : #if no data
                break #stop
            elif len(rows) <=0 and len(rows_set) > 0:
                self.write_data(rows_set)
                break
            rows_set.append(rows)
            cnt += 1
            if cnt >= cpu_count():
                self.write_data(rows_set)
                cnt = 0
                rows_set = []
            self.offset += self.limit

    def write_data(self,rows_set):
        pageReceiver = InboxPageReceiver_Multiprocessing(rows_set)
        pageReceiver.run()
        output_list_set = pageReceiver.result
        if len(output_list_set) > 0: #if something
            for output_list in output_list_set:
                db_writer = ToyBoxWriteDatabase_Analysis(self.dbName) #object
                db_writer.connect() #connect
                db_writer.insert_analyze_temp(output_list) #insert data
                del db_writer #disconnet
        del pageReceiver
        stdout.write(".") #period
# ============== END OF PROGRAM ============== #
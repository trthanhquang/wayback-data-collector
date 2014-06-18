'''
Wayback Machine API Caller
@author: DrTagKim


'''
import requests
'''
> sudo pip install requests
'''
import sys, urllib2, re, time
#
from bs4 import BeautifulSoup as BS #local, TODO - hmm where ...
from Queue import Queue
from threading import Thread
# ===== PROGRAM STARTS =====
class WaybackAPI:
    '''
|  Wayback Machine restarted to distribute API.
|  :)
|  For example,...

    '''
    def __init__(self,loud=False):
        self.loud = loud
    def call(self,url,timestamp = ""):
        assert type(timestamp) == str,"Timestamp should be a string (eg., '20140101')."
        assert type(url) == str, "URL should be a string."
        
        headers = {'connection':'close',
                   'charset':'utf-8',
                   'User-Agent' : 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'}
        wayback_api = "http://archive.org/wayback/available"
        query = {}
        query['url'] = url
        if timestamp != None:
            query['timestamp'] = timestamp
        response = requests.get(url=wayback_api, headers=headers, params=query)
        assert response.status_code == 200, "Connection Error! Response Code: %d" % response.status_code
        json_data = response.json()
        if not self.assert_page_exists(json_data):
            return False
        #processing
        self.data = json_data['archived_snapshots']['closest']
        try:
            if len(self.data['url']) <= 0:
                return False
        except:
            return False
        self.url_found = self.data['url']
        self.timestamp = self.data['timestamp']
        return True
    def assert_page_exists(self,json_code):
        try:
            a = json_code['archived_snapshots']['closest']
        except KeyError:
            return False
        return True

class WbApiPool(Thread):
    def __init__(self, inque, outque, loud = False):
        Thread.__init__(self)
        self.inque = inque
        self.outque = outque
        self.loud = loud
    def terminate(self):
        self.inque.put((None,None,))
    def run(self):
        while 1:
            if self.loud:
                sys.stdout.write("^")
                sys.stdout.flush()
            url,timestamp = self.inque.get()
            if url == None:
                self.inque.task_done()
                break
            wp = WaybackAPI()
            if wp.call(url,timestamp):
                self.outque.put((url,timestamp,wp.url_found,wp.timestamp))
            else:
                self.outque.put((url,timestamp,'NA','NA'))
            if self.loud:
                sys.stdout.write("$")
                sys.stdout.flush()
            self.inque.task_done()

class Navigator:
    def queue_to_list(self,queue_data):
        """
    Queue to list
        """
        list_data = []
        while True:
            try:
                list_data.append(queue_data.get_nowait())
            except:
                break
        return list_data
    def navigate(self, url, queue, depth=2):
        """
|  For example, you can use recursion, BUT it is too slow.
|  So think about multithreading! There are several ways to solve performance problems.
        """
        namespace = "http://web.archive.org"
        if depth <= 0:
            return 1
        else:
            headers = {'connection':'close',
                       'charset':'utf-8',
                       'User-Agent' : 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'}
            try:
                response = requests.get(url=url,headers=headers)
                #request = urllib2.Request(url,None,headers)
                #response = urllib2.urlopen(request,None,timeout = 60)
            except:
                sys.stdout.write("!")
                return 1
            #html = response.read()
            html = response.text
            soup = BS(html,'html.parser')
            #con.close()
            links_all = soup('a')
            links_sub = []
            
            for link in links_all:
                try:
                    link['href']
                except:
                    continue
                if not link['href'].startswith(namespace):
                    links_sub.append("%s%s"%(namespace,link['href'],))
            depth -= 1
            sys.stdout.write(".")
            queue.put(soup)
            for link in links_sub:
                self.navigate(link,queue,depth) #recursion
    def run(self,url,depth=2):
        q = Queue()
        self.navigate(url,q,depth = depth)
        if q.qsize() > 0:
            rv = self.queue_to_list(q)
            return rv
        else:
            return []



class WaybackPagePool(Thread):
    """
Multithreading for WebReader
    """
    def __init__(self, queue_address, queue_page_source,
                timeout = 60, loud = False, politeness = 0,
                soup = False):
        Thread.__init__(self)
        self.queue_address = queue_address
        self.queue_page_source = queue_page_source
        self.timeout = timeout
        self.loud = loud
        self.politeness = politeness
        self.soup = soup
    def terminate(self):
        self.queue_address.put((None, None, None, None)) # url,timestamp,page_url,actual_timestamp
    def run(self):
        while True:
            url, timestamp, target_url, actual_timestamp = self.queue_address.get()
            if url == None:
                self.queue_address.task_done()
                break
            wr = WebReader2(target_url,timeout = self.timeout)
            page = wr.read(soup = self.soup)
            self.queue_page_source.put_nowait((url,target_url,page,))
            if self.loud:
                sys.stdout.write(".")
                sys.stdout.flush()
            time.sleep(self.politeness)
            self.queue_address.task_done()

class WebReader2:
    FAILED = '0'
    NOPAGE = '-1'
    def __init__(self,url = None, timeout = 60, loud = False):

        self.url = url
        self.timeout = timeout
        self.encoding = ""
        self.headers = { 'User-Agent' : 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11',
                         'connection' : 'close',
                         'charset'    : 'utf-8'}
        self.loud = loud
        self.text = ''
        self.soup = None
    def read(self,url = None,parameters = None,soup = False, quietly = False):
        if self.url == None and url == None:
            self.text = "no url"
            return self.text
        if url != None:
            self.url = url
        try: #try resquest (get or post)
            con = requests.get(self.url,
                                timeout=self.timeout,
                                headers = self.headers,
                                params = parameters)
            self.connection_status = con.status_code
            self.encoding = con.encoding
            if self.connection_status == requests.codes.ok:
                self.text = con.text
                if self.loud:
                    print "[INFO] Page is successfully read."
                if soup:
                    if self.loud:
                        print "[INFO] Beautiful soup parsing completed."
                    self.soup = BS(self.text,'html.parser')
            else:
                if self.loud:
                    print "[ERROR] Connection failure. Check connection_status"
                self.text = "0" #which means, failed

        except:
            if self.loud:
                print "[ERROR] Server cannot be found."
            self.text = '-1' #which means, bad connection
        self.text = unicode(self.text)
        if not quietly:
            return self.text
    def export_html_gz(self,gzip_file):
        """
        Export html text to gz file
        """
        import os.path
        fsplit = os.path.splitext(gzip_file)
        if not fsplit[1].endswith('gz'):
            gzip_file = "%s%s" % (gzip_file,'.gz',)
        f = gzip.open(gzip_file,'wb')
        #f.write(self.text)
        f.write(self.text.encode('utf-8'))
        f.close()
    def import_html_gz(self,gzip_file,soup = False, quietly = True):
        """
        Import html gz file into string
        """
        f = gzip.open(gzip_file)
        self.text = f.read()
        f.close()
        self.text = self.text.decode('utf-8')
        if soup:
            self.soup = BS(self.text,'html.parser')
        if not quietly:
            return self.text

def run_web_reader_pool(address_list,n_pool = 4,loud = False, politeness = 0, soup = False):
    qin = list_to_queue(address_list) # url,timestamp,page_url,actual_timestamp
    qout = Queue()
    tasks = []
    if len(address_list) < n_pool:
        n_pool = len(address_list)
    for _ in range(n_pool):
        wrp = WaybackPagePool(qin,qout,timeout=60,loud = loud,soup = soup, politeness = politeness)
        wrp.setDaemon(True)
        wrp.start()
        tasks.append(wrp)
    qin.join()
    for task in tasks:
        task.terminate()
    result = queue_to_list(qout)
    return result

def queue_to_list(queue_data):
    """
Queue to list
    """
    list_data = []
    while True:
        try:
            list_data.append(queue_data.get_nowait())
        except:
            break
    return list_data
def list_to_queue(list_data):
    """
List to Queue
    """
    queue = Queue()
    map(lambda x : queue.put(x), list_data)
    return queue

def inventory_page(url,d_from,d_end,n_pool=4, loud = False):
    inque = Queue()
    outque = Queue()
    for year in range(d_from,d_end + 1):
        for month in range(1,13):
            inque.put((url,"%04d%02d15"%(year,month,)))
    tasks = []
    inque_size = inque.qsize()
    assert inque_size > 0, "No input!"
    if inque_size < n_pool:
        n_pool = inque_size
    for _ in range(n_pool):
        wbapi = WbApiPool(inque,outque,loud = loud)
        wbapi.setDaemon(True)
        wbapi.start()
        tasks.append(wbapi)
    inque.join() #wait till finish job
    for task in tasks:
        task.terminate()
    input_list = queue_to_list(outque)
    rv = run_web_reader_pool(input_list, n_pool = n_pool, loud = loud)
    return rv
    

# Example code...
def sample():
    url_goal = "http://www.nus.edu.sg"
    wp = WaybackAPI()
    if wp.call(url_goal,'20140601'):
        print "Found: %s" % (wp.url_found,)
        print "Near time: %s" % (wp.timestamp,)
    else:
        print "Failed."
    url_navigate = wp.url_found
    nav = Navigator()
    html_soup_bowls = nav.run(url_navigate, depth = 2)
    return html_soup_bowls



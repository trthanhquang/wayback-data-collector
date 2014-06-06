#-------------------------------------------------------------------------------
# Name:        web.py
# Purpose:     Access to Web
# Dependencies: Requests (see also: http://docs.python-requests.org/en/latest/#)
# Author:      drtagkim
#-------------------------------------------------------------------------------

import requests
import gzip
import cPickle
import re
from threading import Thread
from bs4 import BeautifulSoup as BS
import sys,time
from Queue import Queue
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait

#---------------------------------------------------------------
class WebReaderPool(Thread):
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
        self.queue_address.put(None)
    def run(self):
        while True:
            url = self.queue_address.get()
            if url == None:
                self.queue_address.task_done()
                break
            wr = WebReader2(url,timeout = self.timeout)
            page = wr.read(soup = self.soup)
            self.queue_page_source.put_nowait((url,page,))
            if self.loud:
                sys.stdout.write("\rQueue size = %d"%self.queue_address.qsize())
            time.sleep(self.politeness)
            self.queue_address.task_done()
def list_to_queue(list_data):
    """
List to Queue
    """
    queue = Queue()
    map(lambda x : queue.put(x), list_data)
    return queue

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
def run_web_reader_pool(address_list,n_pool = 4,loud = False, politeness = 0, soup = False):
    """
Helper method, address (list) to [(url,page)]
    """
    qin = list_to_queue(address_list)
    qout = Queue()
    tasks = []
    if len(address_list) < n_pool:
        n_pool = len(address_list)
    for _ in range(n_pool):
        wrp = WebReaderPool(qin,qout,timeout=60,loud = loud,soup = soup, politeness = politeness)
        wrp.setDaemon(True)
        wrp.start()
        tasks.append(wrp)
    qin.join()
    for task in tasks:
        task.terminate()
    result = queue_to_list(qout)
    return result
class WebReader2:
    """
If you need to reviwe a process, turn on loud as True.

You do not have to input 'url' here. Input URL address when you call read() function.
    """
    FAILED = '0'
    NOPAGE = '-1'
    def __init__(self,url = None, timeout = 60, loud = False):

        self.url = url
        self.timeout = timeout
        self.encoding = ""
        self.headers = { 'User-Agent' : 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11',
                         'connection' : 'close' }
        self.loud = loud
        self.text = ''
        self.soup = None
    def read(self,url = None,parameters = None,soup = False, quietly = False):
        """
If you do not specify a URL address before, input the infomation here.

If you need to analyze the page, turn on soup as True.

See also, bs4 (BeautifulSoup).
        """
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
class PhantomBrowser:
    """
#Example ~ send keys
elem = driver.find_element_by_name("q")
elem.send_keys("selenium")
elem.click()

#Option
select = Select(driver.find_element_by_name('name'))
select.select_by_index(index)
select.select_by_visible_text("text")
select.select_by_value(value)

select = Select(driver.find_element_by_id('id'))
select.deselect_all()


    """
    def __init__(self):
        """
>>> pb = PhantomBrowser()
        """
        from selenium import webdriver
        self.driver = webdriver.PhantomJS()
        self.driver.set_window_size(1024,768)

    def goto(self,url):
        self.driver.get(url)

    def capture(self,file_location):
        if file_location == None or len(file_location) == 0:
            print "Input proper file_location"
            return
        self.driver.save_screenshot(file_location)
        return "screen captured: %s" % file_location

    def css_selector_elements(self,css_pattern):
        return self.driver.find_elements_by_css_selector(css_pattern)

    def css_selector_element(self,css_pattern):
        return self.driver.find_element_by_css_selector(css_pattern)

    def xpath_element(self,xpath_pattern):
        return self.driver.find_element_by_xpath(xpath_pattern)

    def xpath_elements(self,xpath_pattern):
        return self.driver.find_elements_by_xpath(xpath_pattern)

    def page_source_save(self,file_location):
        if file_location == None or len(file_location) == 0:
            print "Input proper file_location"
            return
        import codecs
        f = codecs.open(file_location,'w','utf-8')
        f.write(self.driver.page_source)
        f.close()
        return "page source: %s" % file_location

    def get_page_source(self):
        return self.driver.page_source

    def execute_javascript(self,script):
        self.driver.execute_script(script)
    def wait_ajax(self,driver):
        try:
            return 0 == driver.execute_script("return jQuery.active")
        except WebDriverException:
            pass
    def check_scroll_complete_ajax(self):
        try:
            return self.driver.execute_script("return $(document).height() == $(window).height()+$(window).scrollTop();")
        except WebDriverException:
            pass
    def scroll_down(self,patient=30):
        script = "window.scrollTo(0, document.body.scrollHeight);"
        self.execute_javascript(script)
        WebDriverWait(self.driver,patient).until(self.wait_ajax,"Timeout waiting for page to load")
        #time.sleep(patient)
    def __del__(self):
        """
>>> del pb
        """
        self.driver.quit()

class BSHelper:
    def __init__(self):
        pass
    def findTextContain(self,soup,text_string):
        tags = soup.find_all(text = re.compile(text_string)) #bs4.element.NavigableString (inherits string)
        tags_list = map(lambda x : x.strip(), tags)
        return tags_list

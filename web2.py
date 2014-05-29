#-------------------------------------------------------------------------------
# Name:        web.py
# Purpose:     Access to Web
#
# Author:      drtagkim
#
# Created:     22-07-2013
# Updated:    18-10-2013
# Copyright:   Dr. Taekyung Kim
# Licence:     private use
#-------------------------------------------------------------------------------

import urllib2, sys, time, hashlib, zlib
from threading import Thread
from Queue import Queue

class Marker:
    def marker_go(cls):
        sys.stdout.write(".")

    def marker_nogo_unicode(cls):
        sys.stdout.write("u")

    def marker_nogo_connection(cls):
        sys.stdout.write("c")

    Marker_go = classmethod(marker_go)
    Marker_nogo_unicode = classmethod(marker_nogo_unicode)
    Marker_nogo_connection = classmethod(marker_nogo_connection)

class WebReader:
    def __init__(self, url, timeout=60, loud = False, encoding='utf-8'):
        self.url = url
        self.timeout = timeout
        headers = { 'User-Agent' : 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11' }
        self.req = urllib2.Request(self.url, None, headers)
        self.loud = loud
        self.encoding = encoding

    def check_connection(self):
        check_result = True
        try:
            self.connection = urllib2.urlopen(self.req,None,timeout = self.timeout)
        except:
            check_result = False
        return check_result

    def check_html_doc(self):
        check_result = True
        if self.connection.info().type != "text/html":
            check_result = False
        return check_result

    def read_as_unicode(self):
        html_unicode = ""
        #page read
        try:
            page_source = self.connection.read()
            if self.loud:
                Marker.Marker_go()
            self.connection.close()
            #unicode conversion
            try:
                html_unicode = unicode(page_source,self.encoding)
            except:
                Marker.Marker_nogo_unicode()
        except:
            Marker.Marker_nogo_connection()

        return html_unicode

    def politeness(self,sleeping_time):
        if self.loud:
            sys.stdout.write("_") #sleep
        time.sleep(sleeping_time)
        if self.loud:
            sys.stdout.write("^") #wakeup

    def run(self,sleeping_time=0):
        html_unicode = ""
        trial = 5
        while not self.check_connection():
            trial -= 1
            sys.stdout.write("[%d] Connection lost.\n" % trial)
            time.sleep(30)
            if trial < 0:
                assert False, "Connection denied"
        self.check_html_doc()
        html_unicode = self.read_as_unicode()
        if sleeping_time > 0:
            self.politeness(sleeping_time)
        return html_unicode

class WebReaderAgent(Thread):
    """
queue_address -> (unique_id,address)
queue_pagesource -> (unique_id,address,page_source)
    """
    def __init__(self,queue_address,queue_page_source,timeout=60,politeness=0):
        Thread.__init__(self)
        self.queue_address = queue_address
        self.queue_page_source = queue_page_source
        self.timeout = timeout
        self.politeness = politeness
    def terminate(self):
        self.queue_address.put(None)

    def run(self):
        while True:
            input_item = self.queue_address.get()
            if input_item == None:
                self.queue_address.task_done()
                break
            #do work
            self.check_input_item(input_item)
            (unique_id,address,) = input_item
            reader = WebReader(address,self.timeout)
            if not reader.check_connection(): #connection
                break
            if not reader.check_html_doc(): #text/html code
                break
            page_source = reader.read_as_unicode()
            if self.politeness > 0: reader.politeness(self.politeness)
            self.queue_page_source.put_nowait((unique_id,address,page_source,))
            self.queue_address.task_done()

    def check_input_item(self,input_item):
        assert isinstance(input_item,tuple), "Items in the input queue must be a tuple."
        assert len(input_item) == 2, "Unique_id and address should be supplied"
        assert input_item[1].lower().startswith("http"), "URL address should start with http.\n"+input_item[1]


def generate_unique_id(url):
    return (hashlib.md5(url)).hexdigest()

def list_to_queue(list_data):
    queue = Queue()
    map(lambda x : queue.put(x), list_data)
    return queue

def queue_to_list(queue_data):
    list_data = []
    while True:
        try:
            list_data.append(queue_data.get_nowait())
        except:
            break
    return list_data

def compress_page_source(web_page):
    return repr(zlib.compress(repr(web_page)))

def decompress_page_source(compressed_web_page):
    return eval(zlib.decompress(eval(compressed_web_page)))


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

    def __del__(self):
        """
>>> del pb
        """
        self.driver.quit()


##if __name__ == "__main__":
##    input_q = Queue()
##    output_q = Queue()
##    print time.asctime()
##    urls = ['http://www.daum.net','http://www.daum.net','http://www.daum.net']
##    for url in urls:
##        input_q.put((generate_unique_id(url),url,))
##    for _ in range(3):
##        t = WebReaderAgent(input_q,output_q)
##        t.setDaemon(True)
##        t.start()
##    input_q.join()
##    print ""
##    print time.asctime()
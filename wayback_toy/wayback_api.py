'''
Wayback Machine API Caller
@author: DrTagKim


'''
import requests
'''
> sudo pip install requests
'''
import sys,urllib2
#
from bs4 import BeautifulSoup as BS #local, TODO - hmm where ...
from Queue import Queue
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



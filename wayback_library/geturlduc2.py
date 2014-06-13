import urllib2
from BeautifulSoup import BeautifulSoup
import re
from collections import OrderedDict

wm = "http://web.archive.org"
wmstart = "http://web.archive.org/web/"
#urlAddr = "www.netscantools.com"
urlAddr = "seriousbit.com"

year = "2014"

if not urlAddr.startswith("http"):
    urlAddr2 = "http://" + urlAddr #if the url does not start with 'http'...
else:
    urlAddr2 = urlAddr


page = urllib2.urlopen(wmstart + year + "0000000000*/" + urlAddr2)
soup = BeautifulSoup(page.read())
links = soup.findAll("a")

link_list = []

for link in links:
    
    if re.match("(.*)%s(.*)" % year, str(link), re.I):
        if not "*" in str(link):
            linkwm = wm + link["href"]
            link_list.append(linkwm)

for final_link in list(set(link_list)):
    print final_link
    

    

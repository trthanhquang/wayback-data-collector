import urllib
from bs4 import BeautifulSoup as BS
from wm2 import WaybackMachine as WB

def main() :
    query = "http://www.bitdefender.com"
    year = "2014"

    w= WB()
    (status,links)=w.get_wayback_timetable_links(query,year)
    
    f = open('snapshots_bitdefender.txt','w')
    for tag in links:
        f.write(links[tag] + '\n')

    f.close()
    '''
    url_parser = urllib.urlopen(query)
    page = url_parser.read()
    soup = BS(page, "html.parser")
    print soup
    
    f.write(soup.prettify().encode('utf8'))
    '''

if __name__ == "__main__":
    main()

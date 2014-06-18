# -*- coding: utf-8 -*-
# file: price_finder.py
'''
|  This program takes in a URL as its input, takes the HTML from the webpage, 
|    searches for a list of products and compiles the name and prices of the products.
|  It does this in two ways:
|    Method 1 - It will search for a table header tag <th> and look for the strings
|      "product" and "price", and store the data
|    Method 2 - If such a table does not exist, then the program will look for
|      tags/attributes

Created on Wed Jun 04 18:09:07 2014

@author: chubbychubs
@contribtor: drtagkim
'''
import urllib2
import BeautifulSoup
import sys

def export_snapshots(all_snapshots):
    """This method takes in a list of tuples (containing date and time of a snapshot created,
    and the URL of the snapshot), and exports them to a csv file called snapshots.csv"""
    f = open('snapshots.csv', 'w')    
    
    for x in all_snapshots:
        temp = str(x).strip('()\'')
        temp = temp.replace('\'', '')
        temp += '\n'
        f.write(temp)
    
    f.close()
       
def collate_archive_links_by_year(html, url):
    """This method takes in the HTML code of the archive records of a particular
    web page. It will return a list of links to the archived web pages. The list
    will be arranged from oldest archived web page to most recent archived web page."""
    #we find the earliest archive of the web page, and the latest archive of the web page
    time_limits = html.find(id='wbMeta').findAll('p')[1].findAll('a')
    least_recent = str(time_limits[0])
    most_recent = str(time_limits[1])
    #we format the string so that we can manipulate the URL
    least_recent = least_recent[least_recent.find('/web/')+len('/web/'):least_recent.find('/http')]
    most_recent = most_recent[most_recent.find('/web/')+len('/web/'):most_recent.find('/http')]
    
    #we want to visit every year's archive of the web page, and we can store each
    #year's archive as a URL in a list
    start_year = int(least_recent[0:4])
    end_year = int(most_recent[0:4])
    snapshots_by_year = ['https://web.archive.org/web/' + least_recent + '*/' + url]
    for x in xrange(1, end_year - start_year + 1):
        temp = str(start_year + x) + most_recent[4:]
        snapshots_by_year.append('https://web.archive.org/web/' + temp + '*/' + url)
    
    return snapshots_by_year

def collate_snapshots(url):
    """This method takes in the URL of a web page (intended to be a URL from archive.org
    that shows the snapshots taken in a year), and returns a list of tuples, each tuple 
    containing the date and time of a snapshot, and the URL that links to the respective 
    snapshot gathered by archive.org"""
    html = convert_to_HTML(url)
    all_links = html.findAll('div', attrs={'class':'month'})
    url_and_date = []
    for x in xrange(12,24):
        links_by_month = all_links[x].findAll('li')
        for y in xrange(len(links_by_month)):
            temp = str(links_by_month[y])
            snapshot_url = 'http://web.archive.org' + temp[temp.find('/web/'):temp.rfind("\"")]
            date_and_time = temp[temp.find('/web/')+len('/web/'):temp.find('/http')]
            url_and_date.append((date_and_time, snapshot_url))
    return url_and_date
        
    
def convert_to_HTML(url):
    """This function takes in the URL of a web page, and then returns a string 
    containing the HTML of the web page"""
    #create the HTML request to the website
    headers = { 'User-Agent' : 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11' ,
                'charset' : 'utf-8',
                'connection' : 'close'}
    request = urllib2.Request(url,None,headers) #you should provide a header definition
    try:
        #create the response object for the HTML request
        response = urllib2.urlopen(request,None,timeout = 60) #timeout for 60 seconds
        #take the HTML from the response object
        assert response.info().type == "text/html", "The data stream is not valid."
        html = response.read()
    #if we come across a 403 or 404 error, the HTML code will be stored in the
    #HTTPError instance, and we just need to extract the HTML code from it
    #this method assumes that it will only come across 403 or 404 errors, but it
    #catches all HTTPErrors.
    except urllib2.HTTPError, e:
        html = e.fp
    except:
        assert False, "Unexpected error: Not 403 or 404. Exiting."
    #convert it into better formatting using BeautifulSoup
    soup = BeautifulSoup.BeautifulSoup(html,'html.parser')
    assert soup != None and len(soup) > 0, "No content"
    return soup

def has_snapshot(html):
    """Given a BeautifulSoup instance containing the HTML of a search result webpage
    from archive.org, this method will search the HTML for an id='error' tag. If there
    is such a tag, that means there is no snapshot of the URL searched for. If there is
    no error tag, that means there is at least one snapshot of the URL searched for. This
    method returns True if there is a snapshot, and False if there is no snapshot."""
    #search for the id="error"
    error = html.find(id='error')
    #if there is id='error' in the HTML, we return false because there is no snapshot
    if error is not None:
        return False
    else:
        return True
    
def has_price_product_table(html):
    """If the HTML string has a table containing information of prices and products,
    this function will return true. If the table does not exist, it will return false
    This function assumes that the headers will be labelled "product" and "price",
    and not other terms such as "catalogue" or "value". """
    #search for all the tables and see if any of them contain the words "price"
    #and "product" in their header
    list_of_tables = html.findAll('table')
    for table in list_of_tables:
        #makes a list of headers in each table
        headers = table.findAll('th')
        #check that the words "product" and "price" are part of the table headers
        s_headers = str(headers).lower()
        if('product' in s_headers and 'price' in s_headers):
            return True;
        else:
            return False;
        
def extract_price_product_table(html):
    """""This method assumes that the HTML string has a table containing information of
    prices and products. It will return a list of tuples containing the products and their
    respective prices. This function assumes that the headers will be labelled "product" 
    and "price", and not other terms such as "catalogue" or "value". """
    list_of_tables = html.findAll('table')
    for table in list_of_tables:
        #makes a list of headers in each table
        headers = table.findAll('thead')
        #run through each table's headers and look for the position of product and price
        for table_headers in headers:
            table_headers = str(table_headers).lower()
            temp = table_headers.split('<th>')

            for index in xrange(len(temp)):
                if 'product' in temp[index]:
                    product_position = index
                if 'price' in temp[index]:
                    price_position = index
        
        assert price_position != product_position, "price_position equals product_position"
        
        #having found the position of product and price in a particular table in a list
        #of tables, we extract the information from that table first
        table_data = table.findAll('td')
def main():
    #prompt user for the URL of the web page
    while 1:
        url = raw_input('Please indicate the URL of the webpage that lists the products and their prices:\n> ')
        #converts it into HTML
        if len(url) <= 0:
            continue
        if not url.startswith("http"):
            continue
        break
    html = convert_to_HTML('http://web.archive.org/web/query?type=urlquery&url=' + url)
    #if there does not exist even a single archive of the webpage
    assert has_snapshot(html), "There are no records of this Webpage at Archive.org"
    #get a list which stores URLs pointing to snapshots that are separated by the year
    #that they were created
    snapshots_by_year = collate_archive_links_by_year(html, url)
    all_snapshots = []
    for year in snapshots_by_year:
        all_snapshots += collate_snapshots(year)
    
    
    
    #try using method 1 to find the list of products and prices
    #if has_price_product_table(html):
    
# ===== END OF PROGRAM =====
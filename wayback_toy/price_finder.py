# -*- coding: utf-8 -*-
#This program takes in a URL as its input, takes the HTML from the webpage, 
#searches for a list of products and compiles the name and prices of the products
#It does this in two ways:
#Method 1 - It will search for a table header tag <th> and look for the strings
#"product" and "price", and store the data
#Method 2 - If such a table does not exist, then the program will look for
#tags/attributes
"""
Created on Wed Jun 04 18:09:07 2014

@author: chubbychubs
"""
import urllib2
import BeautifulSoup

def main():
    #prompt user for the URL of the web page
    url = raw_input('Please indicate the URL of the webpage that lists the products and their prices: ')
    #converts it into HTML
    html = convert_to_HTML(url)
    #if there does not exist even a single archive of the webpage
    if not has_snapshot(html):
        print('There are no records of this webpage at archive.org')
        exit
    
    #try using method 1 to find the list of products and prices

def convert_to_HTML(url):
    """This function takes in the URL of a web page, and then returns a string 
    containing the HTML of the web page"""
    #add a User-Agent so that the website doesn't reject a bot visitor
    header = {'User-Agent': 'Mozilla/5.0'}
    #create the HTML request to the website
    request = urllib2.Request(url, headers=header)
    try:
        #create the response object for the HTML request
        response = urllib2.urlopen(request)
        #take the HTML from the response object
        html = response.read()
    #if we come across a 403 or 404 error, the HTML code will be stored in the
    #HTTPError instance, and we just need to extract the HTML code from it
    #this method assumes that it will only come across 403 or 404 errors, but it
    #catches all HTTPErrors.
    except urllib2.HTTPError, e:
        html = e.fp
    except:
        print('Unexpected error: Not 403 or 404. Exiting.')
        exit

    #convert it into better formatting using BeautifulSoup
    soup = BeautifulSoup.BeautifulSoup(html)
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
    table_list = html.findAll('table')
    for table in table_list:
        #makes a list of headers in each table
        headers = table.findAll('th')
        #check that the words "product" and "price" are part of the table headers
        s_headers = str(headers).lower()
        if('product' in s_headers and 'price' in s_headers):
            return True;
        else:
            return False;
        
    
    
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
    
    #try using method 1 to find the list of products and prices

def convert_to_HTML(url):
    """This function takes in the URL of a web page, and then returns a string 
    containing the HTML of the web page"""    
    #create the HTML request to the website
    request = urllib2.Request(url)
    #create the response object for the HTML request
    response = urllib2.urlopen(request)
    #take the HTML from the response object
    html = response.read()
    #convert it into better formatting using BeautifulSoup
    soup = BeautifulSoup.BeautifulSoup(html)
    return soup
    
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
        
    
    
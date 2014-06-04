# -*- coding: utf-8 -*-
#This program takes in a URL as its input, takes the HTML from the webpage, 
#searches for a list of products and compiles the name and prices of the products
#It does this in two ways:
#Number 1 - It will search for a table header tag <th> and look for the strings
#"product" and "price", and store the data
#Number 2 - If such a table does not exist, then the program will look for
#tags/attributes
"""
Created on Wed Jun 04 18:09:07 2014

@author: chubbychubs
"""
import urllib2
import BeautifulSoup

def main():
    #prompt user for the URL of the web page
    print('test')
    url = raw_input('Please indicate the URL of the webpage that lists the products and their prices')
    #converts it into HTML
    html = convert_to_HTML(url)


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
    
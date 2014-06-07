from bs4 import BeautifulSoup as BS
import re

pageSource = open('pageSource.txt','r')
soup = BS(pageSource)
eles = soup.find_all('p', attrs={'class': re.compile(r'price')})

print eles

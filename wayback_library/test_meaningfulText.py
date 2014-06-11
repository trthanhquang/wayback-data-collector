import urllib2
from BeautifulSoup import BeautifulSoup
import nltk
import re, os
url="http://www.3delite.hu/"
page =urllib2.urlopen(url)

f = open('pageSource.txt','w')
f.write(page.read())
f.close()


html_data = open("pageSource.txt",'r').read()
soup = BeautifulSoup(html_data)
text = str(soup)

#filter out text
raw = nltk.clean_html(text)

#NOT WORKING
#remove double space and tab
#edit = re.sub('[ \t]+' , '', raw)

#edit = re.sub(r'^\s*$' , '', edit)
#filtered = filter(lambda x: not re.match(r'^\s*$', x), raw)

f = open('collectParagraph.txt', 'w')
for line in raw.split('\n') :
    if line.strip() != '' :
        f.write(line + str('\n'))
f.close()

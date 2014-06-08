import urllib2
from bs4 import BeautifulSoup
import nltk
from nltk import FreqDist
import re, os
url="http://www.3delite.hu/"
page =urllib2.urlopen(url)

html_data = open("pageSource.txt",'r').read()
soup = BeautifulSoup(html_data)
text = str(soup)

#filter out text
raw = nltk.clean_html(text)
f = open('collectParagraph.txt', 'w')
for line in raw.split('\n') :
    if line.strip() != '' :
        f.write(line + str('\n'))
f.close()

#words frequency distribution & filter out transition words
para = open('collectParagraph.txt', 'r').read()
para1 = re.sub('[^A-Za-z0-9]+', ' ', str(para))

#1 replace all transtion words with blank
transitionword = {"and": "", "for": "","a": "","an": ""}


transitionword = dict((re.escape(k), v) for k, v in transitionword.iteritems())
pattern = re.compile("|".join(transitionword.keys()))
final = pattern.sub(lambda m: transitionword[re.escape(m.group(0))], str(para1))

#2 words frequency distribution top 100
tokens = nltk.word_tokenize(final)
fdist = FreqDist(tokens)
vocab = fdist.keys()

for x in vocab[:100]:
    print x

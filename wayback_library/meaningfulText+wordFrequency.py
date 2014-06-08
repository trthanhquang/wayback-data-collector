import collections
import urllib2
from BeautifulSoup import BeautifulSoup
import nltk
from nltk import FreqDist
import re, os

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
#filter out punctuation
para1 = re.sub('[^A-Za-z0-9]+', ' ', str(para))
para1 = para1.lower()
#para1 = re.sub('[a-zA-Z0-9]{2,}', '', str(para))

#1 replace all transtion words with blank
#transitionword = {"and": "", "for": "","a": "","an": ""}
transitionword = collections.defaultdict()
with open('linkingWords.txt') as f:
    lines = [l.strip() for l in f if l.strip()]
for word in lines:
    transitionword[word] = ("");

transitionword = dict((re.escape(k), v) for k, v in transitionword.iteritems())
pattern = "|".join("\\b%s\\b"%re.escape(p) for p in transitionword)
final = re.sub(pattern, lambda m: transitionword.get(m), str(para1))
#print pattern

#2 words frequency distribution top 100
tokens = nltk.word_tokenize(final)
fdist = FreqDist(tokens)
vocab = fdist.keys()

for x in vocab[:100]:
    print x

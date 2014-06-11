import re
import nltk
from nltk import FreqDist
transitionword = {"and": "", "love": ""}
transitionword = dict((re.escape(k), v) for k, v in transitionword.iteritems())
#pattern = re.compile("|".join("\b%s\b" %transitionword.keys()))
pattern = "|".join("\\b%s\\b"%re.escape(p) for p in transitionword)
para = open('collectParagraph.txt', 'r').read()
#para1 = "and I will always love_love you andand I will always love you and I "
para1 = re.sub('[^A-Za-z0-9]+', ' ', str(para))
#final = re.sub(pattern, lambda m: transitionword[re.escape(m.group(0))], str(para1))
#final = filter(lambda x: re.escape(x) not in transitionword, [x for x in set(re.split("[\s:/,.:]", para1))])
#print str(pattern)
final = re.sub(pattern, lambda m: transitionword.get(m), str(para1))
#print final
tokens = nltk.word_tokenize(final)
fdist = FreqDist(tokens)
vocab = fdist.keys()

for x in vocab[:100]:
    print x

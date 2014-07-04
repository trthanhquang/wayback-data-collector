#======================================================#
# HELPER, NLTK Module
#======================================================#

from nltk import Text
from nltk.probability import FreqDist
from nltk import word_tokenize
import sys
import nltk

def read_make_nltk_text(raw):
    """
Input string text, you will get Text obj!
    """
    tokens = word_tokenize(raw)
    return Text(tokens)

def reset_stdout():
    sys.stdout = sys.__stdout__

class MsgCatcher:
    def __init__(self):
        self.content = []
    def write(self,string):
        self.content.append(string)
    def get_msg(self):
        return "".join(self.content)

def get_concordance(text,word,width=79,lines=25):
    """
width: coverage
lines: how many lines should be shown?
return: str object
    """
    msg = MsgCatcher()
    sys.stdout = msg
    text.concordance(word, width = width, lines = lines)
    reset_stdout()
    return msg.get_msg()

def get_similar(text,word,num=20):
    """
NLTK similar function
return value: str object
    """
    msg = MsgCatcher()
    sys.stdout = msg
    text.similar(word, num = num)
    reset_stdout()
    return msg.get_msg()

def get_collocation(text,num=20,window_size=2):
    """
    """
    msg = MsgCatcher()
    sys.stdout = msg
    text.collocations(num=num,window_size=window_size)
    reset_stdout()
    return msg.get_msg()

def find_all_from_text(text,pattern):
    """
Find instances of the regular expression in the text.
The text is a list of tokens, and a regexp patterns to match
a simgle token must be surrounded by angle brackets.
    """
    msg = MsgCatcher()
    sys.stdout = msg
    text.findall(pattern)
    reset_stdout()
    return msg.get_msg()
import math
def entropy(labels):
    freqdist = nltk.FreqDist(labels) #frequencies
    probs = [freqdist.freq(l) for l in freqdist]
    return abs(sum([p*math.log(p,2) for p in probs]))


import urllib2

url="http://www.3delite.hu/"
page =urllib2.urlopen(url)

f = open('pageSource1.txt','w')
f.write(page.read())
f.close()

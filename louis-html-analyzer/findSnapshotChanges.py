from compareSnapshot import *
from htmlAnalyzer import *

from stub_crawl import *
from stub_database import *

'''from database import * #!
from crawl import * #!


mock_crawledList = None
mock_htmlList = None
class mock_crawler:
	def __init__(self,itemID):
		global mock_htmlList,mock_crawledList
		olddb = database()
		mock_htmlList = []
		mock_crawledList = []

		html_list = olddb.getHTML(itemID)
		for date,html in html_list:
			mock_htmlList.append(html)
			mock_crawledList.append(0)

		self.downloadCount = 0
	def crawl(self,indexList):
		download = False
		for i in indexList:
			if(mock_crawledList[i]==0):
				mock_crawledList[i]=1
				download = True
		if download:
			self.downloadCount = self.downloadCount + 1
	def getNumberOfSnapshots(self):
		global mock_htmlList
		return len(mock_htmlList)

class mock_database:
	def __init__(self):
		pass
	def getCrawledIndexes(self):
		l = []
		for i in range(len(mock_htmlList)):
			if mock_crawledList[i] == 1:
				l.append(i)
		return l
	def getHTML(self,index):
		global mock_htmlList
		return mock_htmlList[index]

'''

digLevel = 6
db = None
crawler = None

# errorList = ["""?????? ?????????????? ""","Bad Request",
# 	"Got an HTTP 302 response at crawl time"]
def isTextInSnapshot(index,searchString):
	html = db.getHTML(index)
	analyzer = htmlAnalyzer(html)

	# for errorString in errorList:
	# 	if(analyzer.searchText(errorString)!=-1):
	# 		return False

	if(analyzer.searchText(searchString)!=-1):
		return True
	else:
		return False

def refineSearchRange(lo,hi,searchString):
	indexList = db.getCrawledIndexes()
	for index in indexList:
		if (index <lo):
			continue
		if(isTextInSnapshot(index,searchString)):
			lo = index
		else:
			hi = index
			break

	# print 'update range from %s to %s'%(lo,hi)
	return (lo,hi) 

def getBinarySearchIndex(lo,hi,level):
	indexList = []
	if level == 0:
		return indexList
	mid = lo + (hi-lo)/2
	indexList.append(mid)

	indexList.extend(getBinarySearchIndex(lo,mid,level-1))
	indexList.extend(getBinarySearchIndex(mid,hi,level-1))
	return set(indexList)

def binarySearchDiff(lo, hi,searchString):
	global crawler,digLevel
	
	crawler.crawl(getBinarySearchIndex(lo,hi,digLevel))

	if(isTextInSnapshot(hi,searchString)):
		return -1

	level = 0
	while(lo<=hi):
		if(level == digLevel):
			print 'additional dig at (%s,%s)'%(lo,hi)
			level = 0
			crawler.crawl(getBinarySearchIndex(lo,hi,digLevel))

		mid = lo+(hi-lo)/2
		print 'lo= %s, hi=%s, mid=%s'%(lo,hi,mid)
		if(not isTextInSnapshot(mid,searchString)):
			hi = mid -1
		else:
			lo = mid +1

		digLevel = digLevel +1
	return lo

if __name__ == '__main__':
	#global db,crawler
	# db = mock_database()
	db = database()

	# itemID = int(raw_input('Enter itemID: '))
	# appName = db.getItemName(itemID)
	#* Assume correct itemID
	
	itemID = 3401

	# crawler = mock_crawler(itemID)
	crawler = Crawler(itemID)

	#Initialize search ranges
	lo = 0
	endIndex = crawler.getNumberOfSnapshots()-1
	print endIndex
        
	#Prepare snapshots for first search
	downloadList = getBinarySearchIndex(lo,endIndex,digLevel)
	crawler.crawl(downloadList)
	print 'start binary search'

	#Start Binary Search
	while(lo!=-1):
		html = db.getHTML(lo)
		openHTML(html)
		#enter searchString for each version
		searchString = str(raw_input('Enter search string: '))

		(lo,hi)=refineSearchRange(lo,endIndex,searchString)
		print lo,hi

		lo = binarySearchDiff(lo,hi,searchString)
		print lo
		# break #test for 1 only
	

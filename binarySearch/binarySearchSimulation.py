from bisect import bisect_left
from Queue import *
import random

randomSeed = 123456789
# randomSeed = random.random()*123456789

noVersion = 10
listSize = 200

itemList = None #url list
crawledlist = None #downloaded page
downloadCount = None

def init():
	global itemList,crawledlist, downloadCount
	newList = []
	crawledlist = []
	downloadCount = 0
	random.seed(randomSeed)
	for i in range(listSize):
		newItem = int(random.random()*noVersion)
		newList.append(newItem)
		crawledlist.append(0)

	itemList = sorted(newList)

def download(dlist):
	global downloadCount
	download = False
	for i in dlist:
		if(crawledlist[i]==0):
			crawledlist[i]=1
			download = True
	if download:
		downloadCount = downloadCount+1

def getDivideIndex(lo,hi,level):
	indexList = []
	if level == 0:
		return indexList
	mid = lo + (hi-lo)/2
	indexList.append(mid)

	indexList.extend(getDivideIndex(lo,mid,level-1))
	indexList.extend(getDivideIndex(mid,hi,level-1))
	return set(indexList)

def binarySearchDiff(lo, hi):
	digLevel = 6
	download(getDivideIndex(lo,hi,digLevel))

	searchItem = itemList[lo]
	if(itemList[hi]==searchItem):
		return -1

	while(lo<=hi):
		if(digLevel == 0):
			print 'additional dig at (%s,%s)'%(lo,hi)
			digLevel = 6
			download(getDivideIndex(lo,hi,digLevel))

		mid = lo+(hi-lo)/2
		# print 'lo= %s, hi=%s, mid=%s'%(lo,hi,mid)
		if(itemList[mid]!=searchItem):
			hi = mid -1
		else:
			lo = mid +1

		digLevel = digLevel -1
	return lo

def refineSearchRange(lo,hi):
	searchItem = itemList[lo]

	for i in range(lo,hi,1):
		if(crawledlist[i]==1):
			if(itemList[i]==searchItem):
				lo = i
			else:
				hi = i
				break

	# print 'update range from %s to %s'%(lo,hi)
	return (lo,hi)
def normalSearch():
	init()
	# print itemList
	
	lo = 0
	endIndex = len(itemList)-1
	
	while(lo!=-1):
		hi = endIndex
		# (lo,hi)= refineSearchRange(lo,hi)
		lo = binarySearchDiff(lo,hi)
		# print 'index=%s, item=%s'%(lo,itemList[lo])
	
	visited = sum(crawledlist)
	percentage = 100.0*visited/len(itemList)
	print 'normalSearch: download {2} times ({0} snapshots downloaded, {1:.3g}%)'.format(visited,percentage,downloadCount)
def advanceSearch():
	init()
	# print itemList
	
	lo = 0
	endIndex = len(itemList)-1
	
	while(lo!=-1):
		hi = endIndex
		(lo,hi)= refineSearchRange(lo,hi)
		lo= binarySearchDiff(lo,hi)
		print 'index=%s, item=%s'%(lo,itemList[lo])
	
	visited = sum(crawledlist)
	percentage = 100.0*visited/len(itemList)
	print 'advanceSearch: download {2} times ({0} snapshots downloaded, {1:.3g}%)'.format(visited,percentage,downloadCount)


def main():
	global noVersion,listSize
	noVersion = 20
	listSize = 2000

	# normalSearch()
	advanceSearch()

if __name__ == '__main__':
	main()
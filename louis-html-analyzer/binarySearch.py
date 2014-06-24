from bisect import bisect_left

import random

# randomSeed = 123456789
randomSeed = random.random()*123456789

noVersion = 10
listSize = 200

itemList = []
visitedList = []

def init():
	global itemList,visitedList
	newList = []
	visitedList = []
	random.seed(randomSeed)
	for i in range(listSize):
		newItem = int(random.random()*noVersion)
		newList.append(newItem)
		visitedList.append(0)

	itemList = sorted(newList)
	
def binarySearchDiff(lo, hi):
	searchItem = itemList[lo]
	visitedList[lo] = 1
	
	if(itemList[hi]==searchItem):
		visitedList[hi] = 1
		return -1

	while(lo<=hi):
		mid = lo+(hi-lo)/2
		# print 'lo= %s, hi=%s, mid=%s'%(lo,hi,mid)
		visitedList[mid]=1
		if(itemList[mid]!=searchItem):
			hi = mid -1
		else:
			lo = mid +1
	return lo

def refineSearchRange(lo,hi):
	searchItem = itemList[lo]

	for i in range(lo,hi,1):
		if(visitedList[i]==1):
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
	
	visited = sum(visitedList)
	percentage = 100.0*visited/len(itemList)
	print 'normalSearch: visited = {0}, percentage = {1:.3g}%'.format(visited,percentage)

def resetVisitedList():
	for i in range(len(visitedList)):
		visitedList[i]=0

def advanceSearch():
	init()
	# print itemList
	
	lo = 0
	endIndex = len(itemList)-1
	
	while(lo!=-1):
		hi = endIndex
		(lo,hi)= refineSearchRange(lo,hi)
		lo = binarySearchDiff(lo,hi)
		# print 'index=%s, item=%s'%(lo,itemList[lo])
	
	visited = sum(visitedList)
	percentage = 100.0*visited/len(itemList)
	print 'advanceSearch: visited = {0}, percentage = {1:.3g}%'.format(visited,percentage)


def main():
	global noVersion,listSize
	noVersion = 20
	listSize = 2000

	normalSearch()
	advanceSearch()

if __name__ == '__main__':
	main()
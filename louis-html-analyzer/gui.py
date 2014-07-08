import sys
from PyQt4 import QtCore, QtGui, uic
from multithreadCrawler import *
from snapshotAnalyzer import *

class crawlingThread(QtCore.QThread):
    #indexFinished = QtCore.Signal(int,int)
    def __init__(self,inputURL,parent=None):
        QtCore.QThread.__init__(self,parent)
        self.inputURL = inputURL
        self.snapshotList = []
        
    def run(self):
        print 'start Crawling from %s'%self.inputURL
        urlList = getURLs(self.inputURL)
        print "%s Snapshots found"%len(urlList)
        self.snapshotList = getSnapshots(urlList,num_thread = 20)
        
    def getSnapshotList(self):
        return self.snapshotList

class GUI(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.ui = uic.loadUi('snapshotCompare.ui')
        self.ui.show()

        self.ui.urlText.setText("http://www.aone-video.com/avi.htm")
        self.ui.nameText.setText("Ultra AVI Converter")
        self.ui.startButton.clicked.connect(self.startCrawling)

        self.ui.startSearchButton.clicked.connect(self.startSearching)

        self.ui.errButton.clicked.connect(self.pageErrorHandler)
        self.ui.diffButton.clicked.connect(self.versionDiffHandler)

        self.index = 0
        self.total = 0

    def startCrawling(self):
        if (not self.ui.loadFromFile.isChecked()):
            inputURL = str(self.ui.urlText.toPlainText())

            self.thread = crawlingThread(inputURL)
            self.thread.finished.connect(self.finishCrawling)
            self.thread.start()

        else:
            self.finishCrawling()            

    def finishCrawling(self):        
        if (not self.ui.loadFromFile.isChecked()):
            self.snapshotList = self.thread.getSnapshotList()
            self.thread.terminate()

            if self.ui.saveToFile:
                print 'saving to file'
                pickle.dump(self.snapshotList, open("data.p","wb"))
        else:
            self.snapshotList = pickle.load(open("data.p","rb"))

        self.index = 0
        self.total = len(self.snapshotList)
        self.snapshotList[0].openHTML()

    def finishSearching(self):
        print 'Finished searching! Please enter new URL!'
        self.ui.searchText.setText("")
        self.ui.urlText.setText("")
        self.ui.nameText.setText("")
        self.ui.dateText.setText("")
        self.ui.loadFromFile.setChecked(False)

    def startSearching(self):    
        if self.index == self.total:
            self.finishSearching()

        print 'startSearching...'
        self.keyword = str(self.ui.searchText.toPlainText())
        

        if self.keyword =="":
            print 'Please enter the keyword!'
            return

        print 'keyword = %s'%self.keyword

        while(self.index < self.total):
            snapshot = self.snapshotList[self.index]
            
            self.ui.dateText.setText(snapshot.getDate())

            print '%s/%s. Analyzing %s'%(self.index+1,self.total,snapshot.getDate())

            if snapshot.contain(self.keyword):
                self.index = self.index+1
                print 'OK'
            elif snapshot.contain("Got an HTTP 302 response at crawl time"):
                print 'Error 302! Continue'
            else:
                print 'Unable to find: '+self.keyword
                self.snapshotList[self.index].openHTML()
                break

        if self.index == self.total:
            self.finishSearching()

    def pageErrorHandler(self):
        if self.index == self.total:
            self.finishSearching()

        print 'PageError! continue to search'
        self.index = self.index+1
        self.startSearching

    def versionDiffHandler(self):
        if(self.index >0):
            self.snapshotList[self.index-1].compareHTML(self.snapshotList[self.index])
        else:
            self.snapshotList[0].openHTML()

def main():
    app = QtGui.QApplication(sys.argv)
    try:
        myApp = GUI()
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        print 'KeyboardInterrupt!'
        sys.exit(0)

if __name__ == '__main__':
    main()

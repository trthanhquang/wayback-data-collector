import sys
from PyQt4 import QtCore, QtGui, uic
from multithreadCrawler import *
from snapshotAnalyzer import *

class GUI(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.ui = uic.loadUi('snapshotCompare.ui')
        self.ui.show()

        self.ui.urlText.setText("http://www.aone-video.com/avi.htm")
        self.ui.startButton.clicked.connect(self.startCrawling)

        self.ui.okButton.clicked.connect(self.startSearching)
        self.ui.errButton.clicked.connect(self.pageErrorHandler)

        self.index = 0
        self.total = 0
    def startCrawling(self):
        num_thread = 20

        url = str(self.ui.urlText.toPlainText())
        urlList = getURLs(url)

        self.total = len(urlList)

        self.ui.progressText.setText("0/%s Snapshots"%self.total)
        print "Data Crawling is done! %s Snapshots found"%self.total
        self.snapshotList = getSnapshots(urlList,num_thread = 30)
        self.snapshotList[0].openHTML()

    def startSearching(self):
        self.keyword = str(self.ui.searchText.toPlainText())
        while(self.index < self.total):
            snapshot = self.snapshotList[self.index]
            self.ui.progressText.setText("%s/%s Snapshots"%(self.index,self.total))
            self.ui.dateText.setText(snapshot.getDate())
            print '%s/%s. Analyzing %s'%(self.index,self.total,snapshot.getDate())

            if snapshot.contain(self.keyword):
                self.index = self.index+1
                print 'OK'
            elif snapshot.contain("Got an HTTP 302 response at crawl time"):
                print 'Error 302! Continue'
            else:
                break
    def pageErrorHandler(self):
        print 'PageError! continue to search'
        self.index = self.index+1
        self.startSearching

def main():
    app = QtGui.QApplication(sys.argv)
    try:
        myApp = GUI()
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        print 'KeyboardInterrupt!'
        sys.exit(app.exec_())
        sys.exit()

if __name__ == '__main__':
    main()

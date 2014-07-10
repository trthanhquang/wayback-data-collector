import sys
from PyQt4 import QtCore, QtGui, uic

from multithreadCrawler import *
from snapshotAnalyzer import *
from database import *

import time

class crawlingThread(QtCore.QThread):
    #indexFinished = QtCore.Signal(int,int)
    def __init__(self,inputURL,writeToFile=True,numThread = 20,fileName = "default.pickle",parent=None):
        QtCore.QThread.__init__(self,parent)
        self.inputURL = inputURL
        self.snapshotList = []
        self.writeToFile = writeToFile
        self.numThread = numThread
        self.fileName = fileName

    def run(self):
        print 'Start Crawling from %s'%self.inputURL
        urlList = getURLs(self.inputURL)
        print "%s Snapshots found"%len(urlList)
        self.snapshotList = getSnapshots(urlList,self.numThread)
        print 'Finish Crawling'
        if self.writeToFile:
            print 'Saving to %s'%self.fileName
            pickle.dump(self.snapshotList, open(self.fileName,"wb"))
            print 'Saved!'
    def getSnapshotList(self):
        return self.snapshotList
'''
class searchingThread(QtCore.QThread):
    def __init__(self,parent=None):
        QtCore.QThread.__init__(self,parent)

    def run(self):
        pass
'''

class GUI(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.ui = uic.loadUi('snapshotCompare.ui')
        self.ui.show()

        self.ui.urlText.setText("http://www.aone-video.com/avi.htm")
        self.ui.startButton.clicked.connect(self.startCrawling)
        self.ui.loadFileButton.clicked.connect(self.loadFromFile)
        self.ui.loadDatabaseButton.clicked.connect(self.loadDatabase)


        self.ui.diffButton.clicked.connect(self.versionDiffHandler)
        self.ui.htmlButton.clicked.connect(self.openCurrentHTML)
        self.ui.startSearchButton.clicked.connect(self.startSearching)
        
        self.ui.stopButton.clicked.connect(self.stopSearching)
        
        self.ui.errButton.clicked.connect(self.pageErrorHandler)

        self.ui.comparatorGroup.setDisabled(True)
        self.ui.crawlerGroup.setEnabled(True)
        
        self.index = 0
        self.total = 0
        self.db = database()
        
    def startCrawling(self):
        inputURL = str(self.ui.urlText.toPlainText())
        
        saveOption = self.ui.saveToFile.isChecked()
        threadOption = int(self.ui.threadText.toPlainText())
        
        fname = "default.pickle"
        if saveOption:
            fnameInput = QtGui.QFileDialog.getSaveFileName(self,'Save Pickle File','.',"Pickle File (*.pickle)")
            if fnameInput!="":
                fname = fnameInput

        self.thread = crawlingThread(inputURL,writeToFile=saveOption,numThread=threadOption,fileName = fname)

        self.thread.finished.connect(self.finishCrawling)
        self.thread.start()

    def finishCrawling(self):        
        self.snapshotList = self.thread.getSnapshotList()
        self.thread.terminate()
        self.initSearch()
        
    def loadFromFile(self):
        fname = QtGui.QFileDialog.getOpenFileName(self,'Open Pickle File','.',"Pickle File (*.pickle)")
        try:
            f = open(fname,"rb")
            self.snapshotList = pickle.load(f)
            self.initSearch()
        except Exception,e:
            print "No File selected!%s"%e

    def loadDatabase(self):
        itemID = int(self.ui.itemIDText.toPlainText())
        rows = self.db.getDataList(itemID)
        
        self.snapshotList = []
        for (url,html) in rows:
            self.snapshotList.append(Snapshot(url,html))

        productName = self.db.getItemName(itemID)
        self.ui.nameText.setText(productName)
        
        self.initSearch()

    def initSearch(self):
        self.index = 0
        self.total = len(self.snapshotList)

        if self.total == 0:
            print 'Unable to load! No Snapshot Available!'
            return
        
        self.snapshotList[0].openHTML()
        self.ui.dateText.setText(self.snapshotList[0].getDate())

        self.ui.crawlerGroup.setDisabled(True)
        self.ui.comparatorGroup.setEnabled(True)

        self.ui.progressText.setText("%s/%s"%(self.index,self.total))
        self.ui.progressBar.setValue(int(self.index*100.0/self.total))
 
    def openCurrentHTML(self):
        if self.index == self.total:
            self.finishSearching()
            return

        self.snapshotList[self.index].openHTML()

    def finishSearching(self):
        QtGui.QMessageBox.about(self,"Notification","Finished searching!")        
        print 'Finished searching!'
        self.ui.nameText.setText("")
        self.ui.searchText.setText("")
        self.ui.urlText.setText("")
        self.ui.dateText.setText("")
        self.ui.progressText.setText("{0}/{0}".format(self.total))
        self.ui.comparatorGroup.setDisabled(True)
        self.ui.crawlerGroup.setEnabled(True)

    def startSearching(self):    
        if self.index == self.total:
            self.finishSearching()

        print 'startSearching...'
        self.keyword = str(self.ui.searchText.toPlainText().toUtf8())

        if self.keyword =="":
            print 'Please enter the keyword!'
            return

        # self.ui.comparatorGroup.setDisabled(True)

        print 'keyword = %s'%self.keyword

        loopCount = 0
        while(self.index < self.total):
            loopCount = loopCount +1
            if(loopCount % 5 == 0): #refresh once every 5 snapshots scanned
                QtGui.QApplication.processEvents()
                
            snapshot = self.snapshotList[self.index]
            
            self.ui.dateText.setText(snapshot.getDate())

            print '%s/%s. Analyzing %s'%(self.index+1,self.total,snapshot.getDate())

            if snapshot.contain(self.keyword):
                self.lastOKindex = self.index
                self.index = self.index+1

                self.ui.progressText.setText("%s/%s"%(self.index,self.total))
                self.ui.progressBar.setValue(int(self.index*100.0/self.total))
                print 'OK'

            elif snapshot.contain("Got an HTTP 302 response at crawl time"):
                print 'Error 302! Continue'
                self.index = self.index+1

            else:
                print 'Unable to find: '+self.keyword
                self.ui.searchText.setText("")
                self.snapshotList[self.index].openHTML()
                break

        if self.index == self.total:
            self.finishSearching()
        
        # self.ui.comparatorGroup.setEnabled(True)

    def stopSearching(self):
        self.index = self.total
        self.finishSearching()

    def pageErrorHandler(self):
        if self.index == self.total:
            self.finishSearching()

        print 'PageError at index %s! continue to search'%self.index
        self.index = self.index+1

        self.ui.searchText.setText(self.keyword)
        self.ui.progressText.setText("%s/%s"%(self.index,self.total))
        self.ui.progressBar.setValue(int(self.index*100.0/self.total))

        self.startSearching()

    def versionDiffHandler(self):
        if(self.index >0):
            self.snapshotList[self.lastOKindex].compareHTML(self.snapshotList[self.index])
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

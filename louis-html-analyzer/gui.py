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

        self.ui.urlText.setPlainText("http://www.aone-video.com/avi.htm")
        self.ui.startButton.clicked.connect(self.startCrawling)
        self.ui.loadFileButton.clicked.connect(self.loadFromFile)
        self.ui.loadDatabaseButton.clicked.connect(self.loadDatabase)


        self.ui.diffButton.clicked.connect(self.versionDiffHandler)
        self.ui.htmlOfflineButton.clicked.connect(self.openOfflineHTML)
        self.ui.htmlOnlineButton.clicked.connect(self.openOnlineHTML)
        self.ui.startSearchButton.clicked.connect(self.startSearching)
        
        self.ui.stopButton.clicked.connect(self.stopSearching)
        self.ui.errButton.clicked.connect(self.skipHandler)

        self.ui.comparatorGroup.setDisabled(True)
        self.ui.crawlerGroup.setEnabled(True)

        self.index = 0
        self.total = 0
        self.db = None


        #----------------- Report --------------------
        self.ui.reportSavePriceButton.clicked.connect(self.reportPriceHandler)
        self.ui.reportSaveFeatureButton.clicked.connect(self.reportFeatureHandler)
        self.ui.reportEnableButton.clicked.connect(self.reportEnableHandler)
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
        try:
            self.db = database()
        except Exception,e:
            QtGui.QMessageBox.about(self,"Notification","No Database Available!")
            print "no database Available"
            return

        itemIDstr = self.ui.itemIDText.toPlainText()        
        if itemIDstr == "":
            QtGui.QMessageBox.about(self,"Notification","Please enter itemID!")
            return
        itemID = int(itemIDstr)

        rows = self.db.getDataList(itemID)
        
        self.snapshotList = []
        for (url,html) in rows:
            self.snapshotList.append(Snapshot(url,html))

        productName = self.db.getItemName(itemID)

        if productName == "ItemID not found in database":
            QtGui.QMessageBox.about(self,"Notification","Item ID %s is not in database"%itemID)
            return

        if len(self.snapshotList) == 0:
            homepageURL = self.db.getWebsiteHomepage(itemID)
            
            priceURL = self.db.getWebsitePriceURL(itemID)
            if priceURL == "Free":
                priceURL = ""

            featureURL = self.db.getWebsiteFeatureURL(itemID)
            if featureURL =="ItemID not found in database":
                featureURL = ""

            print homepageURL,priceURL,featureURL
            url = "http://www.google.com"
            QtGui.QMessageBox.about(self,"Notification",
                """
                <p>
                    No Snapshot Available For item {0}!<br>
                    Product Name: \"{1}\"<br>
                    Home Page: <a href= \"{homePage}\"> \"{homePage}\" </a><br>
                    Price URL: <a href= \"{pricePage}\"> \"{pricePage}\"</a><br>
                    Feature URL: <a href= \"{featurePage}\"> \"{featurePage}\" </a>
                </p>
                """.format(itemID,productName,
                    homePage=homepageURL,
                    pricePage=priceURL,
                    featurePage=featureURL))
            print 'Unable to load! No Snapshot Available!'
            return

        self.ui.nameText.setPlainText(productName)
        self.reportAutoFill(itemID=itemID,itemName=productName)
        
        self.initSearch()

    def initSearch(self):
        self.index = 0
        self.total = len(self.snapshotList)
        self.keyword = None

        self.snapshotList[0].openHTML()
        snapshotDate = self.snapshotList[0].getDate()
        self.ui.dateText.setPlainText(snapshotDate)

        self.ui.crawlerGroup.setDisabled(True)
        self.ui.comparatorGroup.setEnabled(True)

        self.ui.progressText.setPlainText("%s/%s"%(self.index,self.total))
        self.ui.progressBar.setValue(int(self.index*100.0/self.total))
 
        self.ui.reportSavePriceButton.setDisabled(True)
        self.ui.reportSaveFeatureButton.setDisabled(True)

    def openOfflineHTML(self):
        if self.index == self.total:
            self.finishSearching()
            return

        self.snapshotList[self.index].openHTML()

    def openOnlineHTML(self):
        if self.index == self.total:
            self.finishSearching()
            return

        self.snapshotList[self.index].openHTML(mode="online")

    def finishSearching(self):
        QtGui.QMessageBox.about(self,"Notification","Finished searching!")        
        print 'Finished searching!'
        self.ui.nameText.setPlainText("")
        self.ui.searchText.setPlainText("")
        self.ui.urlText.setPlainText("")
        self.ui.dateText.setPlainText("")
        self.ui.progressText.setPlainText("{0}/{0}".format(self.total))
        self.ui.comparatorGroup.setDisabled(True)
        self.ui.crawlerGroup.setEnabled(True)
        self.keyword = None

    def startSearching(self):
        self.ui.reportItemNameText.setDisabled(True)
        self.ui.reportPriceText.setDisabled(True)
        self.ui.reportPriceText.setDisabled(True)
        self.ui.reportFeatureText.setDisabled(True)

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
            
            self.ui.dateText.setPlainText(snapshot.getDate())

            print '%s/%s. Analyzing %s'%(self.index+1,self.total,snapshot.getDate())

            if snapshot.contain(self.keyword):
                self.lastOKindex = self.index
                self.index = self.index+1

                self.ui.progressText.setPlainText("%s/%s"%(self.index,self.total))
                self.ui.progressBar.setValue(int(self.index*100.0/self.total))

                self.reportAutoFill(
                    snapshotDate=snapshot.getDate())

                print 'OK'

            elif snapshot.contain("Got an HTTP 302 response at crawl time"):
                print 'Error 302! Continue'
                self.index = self.index+1

            else:
                print 'Unable to find: '+self.keyword
                self.ui.searchText.setPlainText("")
                self.snapshotList[self.index].openHTML()
                break

        if self.index == self.total:
            self.finishSearching()

        self.ui.reportSavePriceButton.setDisabled(False)
        self.ui.reportSaveFeatureButton.setDisabled(False)
        
        # self.ui.comparatorGroup.setEnabled(True)

    def stopSearching(self):
        self.index = self.total
        self.finishSearching()

    def skipHandler(self):
        if self.index == self.total:
            self.finishSearching()

        print 'Skip index %s! continue to search'%self.index
        self.index = self.index+1

        self.ui.progressText.setPlainText("%s/%s"%(self.index,self.total))
        self.ui.progressBar.setValue(int(self.index*100.0/self.total))

        if self.keyword ==None:
            print 'WARN: no keyword!'
        else:
            self.ui.searchText.setPlainText(self.keyword)
            self.startSearching()

    def versionDiffHandler(self):
        if(self.index >0):
            self.snapshotList[self.lastOKindex].compareHTML(self.snapshotList[self.index])
        else:
            self.snapshotList[0].openHTML()

    #------------------------- Report Handler ----------------------------
    def reportAutoFill(self,itemID=None, itemName=None, snapshotDate=None):
        if itemID:
            self.ui.reportIdText.setPlainText(str(itemID))
        if itemName:
            self.ui.reportItemNameText.setPlainText(itemName)
        if snapshotDate:
            self.ui.reportDateText.setPlainText(snapshotDate)

    def reportPriceHandler(self):
        itemID = int(self.ui.reportIdText.toPlainText())
        itemName = str(self.ui.reportItemNameText.toPlainText().toUtf8())
        itemPrice = str(self.ui.reportPriceText.toPlainText().toUtf8())
        snapshotDate = str(self.ui.reportDateText.toPlainText().toUtf8())

        reply = QtGui.QMessageBox.question(self,"Confirmation",
            "Adding itemID %s(%s) price %s on %s to report"%(itemID,itemName,itemPrice,snapshotDate),
            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        if reply==QtGui.QMessageBox.Yes:
            self.db.reportPrice(itemID,itemName,snapshotDate,itemPrice)
            print 'Saved to database'

            self.ui.reportPriceText.setPlainText("")
            self.ui.reportDateText.setPlainText("")
            
            self.ui.reportItemNameText.setDisabled(False)
            self.ui.reportPriceText.setDisabled(False)
            self.ui.reportFeatureText.setDisabled(False)
            
            self.ui.reportSavePriceButton.setDisabled(True)

    def reportFeatureHandler(self):
        itemID = int(self.ui.reportIdText.toPlainText())
        itemName = str(self.ui.reportItemNameText.toPlainText().toUtf8())
        itemFeature = str(self.ui.reportFeatureText.toPlainText().toUtf8())
        snapshotDate = str(self.ui.reportDateText.toPlainText().toUtf8())

        reply = QtGui.QMessageBox.question(self,"Confirmation",
            "ID %s, %s changes on %s in feature is added to report!"%(itemID,itemName,snapshotDate),
            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        
        if reply==QtGui.QMessageBox.Yes:
            self.db.reportFeature(itemID,itemName,snapshotDate,itemFeature)
            print 'saved to database'

            self.ui.reportFeatureText.setPlainText("")
            self.ui.reportDateText.setPlainText("")

            self.ui.reportItemNameText.setDisabled(False)
            self.ui.reportPriceText.setDisabled(False)
            self.ui.reportFeatureText.setDisabled(False)

            self.ui.reportSaveFeatureButton.setDisabled(True)

    def reportEnableHandler(self):
            self.ui.reportIdText.setDisabled(False)
            self.ui.reportItemNameText.setDisabled(False)
            self.ui.reportDateText.setDisabled(False)
            self.ui.reportPriceText.setDisabled(False)
            self.ui.reportFeatureText.setDisabled(False)
            self.ui.reportSaveFeatureButton.setDisabled(False)
            self.ui.reportSavePriceButton.setDisabled(False)

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

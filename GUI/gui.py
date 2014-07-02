import sys
from PyQt4 import QtCore, QtGui, uic

class GUI(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.ui = uic.loadUi('snapshotCompare.ui')
        self.ui.show()

        self.ui.url.setText("http://www.aone-video.com/avi.htm")

        self.ui.startButton.clicked.connect(self.startCrawling)
        #self.ui.url.editingFinished.connect(self.startCrawling)

        # self.ui.okButton.connect(self.searchTextEntered)

    def startCrawling(self):
        num_thread = 20
        
        url = str(self.ui.url.toPlainText())
        urlList = getURLs(url)
        self.ui.status.setText("Found %s Snapshots"%len(urlList))

        snapshotList = []
        urlQueue = Queue()

        for threadId in range(num_thread):
            t = Thread(target = htmlCrawler, args =(threadId,urlQueue,snapshotList,))
            t.daemon = True
            t.start()

        for i in range(len(urlList)):
            url = urlList[i]
            urlQueue.put(url)

        for i in range(num_thread):
            urlQueue.put('stop')

        urlQueue.join()
        
    #def searchTextEntered(self):
        
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

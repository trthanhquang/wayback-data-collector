import shutil, errno, os
from Queue import *
from threading import *

def copyAnything(src, dst):
    try:
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
    except WindowsError as exc: # python >2.5
        if exc.errno == errno.ENOTDIR or exc.errno == errno.ENOENT\
            or exc.errno == errno.EINVAL:
            shutil.copy(src, dst)
        else: raise

def worker(q):
    i = q.get()
    workingDataSet = "MervynList"
    workingDataSetFolder = workingDataSet + "_RENAME_TO_crawling"
    dstFolder = workingDataSet + "P" + str(i) + "_RENAME_TO_crawling"
    copyAnything("crawling", dstFolder)

    copyAnything(workingDataSetFolder + '/db.opt', dstFolder + "/db.opt")
    
    copyAnything(workingDataSetFolder + '/item.frm', dstFolder + "/item.frm")
    copyAnything(workingDataSetFolder + '/item.MYD', dstFolder + "/item.MYD")
    copyAnything(workingDataSetFolder + '/item.MYI', dstFolder + "/item.MYI")

    copyAnything(workingDataSetFolder + '/snapshot_feature.frm', dstFolder + "/snapshot_feature.frm")
    copyAnything(workingDataSetFolder + '/snapshot_feature.par', dstFolder + "/snapshot_feature.par")
    copyAnything(workingDataSetFolder + '/snapshot_feature#P#p' + str(i) + '.MYD', dstFolder + '/snapshot_feature#P#p' + str(i) + '.MYD')
    copyAnything(workingDataSetFolder + '/snapshot_feature#P#p' + str(i) + '.MYI', dstFolder + '/snapshot_feature#P#p' + str(i) + '.MYI')
    
    copyAnything(workingDataSetFolder + '/snapshot_price.frm', dstFolder + "/snapshot_price.frm")
    copyAnything(workingDataSetFolder + '/snapshot_price.par', dstFolder + "/snapshot_price.par")
    copyAnything(workingDataSetFolder + '/snapshot_price#P#p' + str(i) + '.MYD', dstFolder + '/snapshot_price#P#p' + str(i) + '.MYD')
    copyAnything(workingDataSetFolder + '/snapshot_price#P#p' + str(i) + '.MYI', dstFolder + '/snapshot_price#P#p' + str(i) + '.MYI')

    copyAnything(workingDataSetFolder + '/report_price.frm', dstFolder + "/report_price.frm")
    copyAnything(workingDataSetFolder + '/report_price.par', dstFolder + "/report_price.par")

    copyAnything(workingDataSetFolder + '/report_feature.frm', dstFolder + "/report_feature.frm")
    copyAnything(workingDataSetFolder + '/report_feature.par', dstFolder + "/report_feature.par")
    
    copyAnything(workingDataSetFolder + '/status.frm', dstFolder + "/status.frm")
    copyAnything(workingDataSetFolder + '/status.MYD', dstFolder + "/status.MYD")
    copyAnything(workingDataSetFolder + '/status.MYI', dstFolder + "/status.MYI")
    
    print "Done copying part " + i

if __name__ == '__main__':
    partQueue = Queue()
    for i in range(0, 5):
        t = Thread(target = worker, args = (partQueue,))
        t.daemon = True
        t.start()

    for i in range(0, 5):
        partQueue.put(i)
        
    partQueue.join()

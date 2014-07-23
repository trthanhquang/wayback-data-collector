import urllib2
from database import *
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

driver = webdriver.Chrome();
class CrawlEvaluator(object):
    wbm_prefix = "http://web.archive.org/web/*/"
    
    def __init__ (self, itemID):
        self.itemID = itemID
        self.db = database()
        url = self.db.getWebsitePriceURL(itemID)
        self.url_list = []
        if url is not None and "." in url :    
            if not url.startswith("http"):
                self.price_url = "http://" + url
            else:
                self.price_url = url
        else:
            self.price_url = None

        url = self.db.getWebsiteFeatureURL(itemID)
        self.sameLink = False
        if url is not None and "." in url:
            if not url.startswith("http"):
                self.feature_url = "http://" + url
            else:
                self.feature_url = url

            if (url == self.db.getWebsitePriceURL(itemID)):
                self.sameLink = True
        else:
            self.feature_url = None
        
    def __analyzeWBMSummaryPage (self):
        try:
            global driver
            if self.feature_url is None:
                numberOfFeatureSnapshots = 0
            else:
                driver.get(self.wbm_prefix + self.feature_url)
                element = driver.find_element_by_xpath("//div[@id='wbMeta']/p[2]/strong")
                numberOfFeatureSnapshots = int(re.sub("[^0-9]", "", element.text)) + 1
            if self.price_url is None:
                numberOfPriceSnapshots = 0
            else:
                driver.get(self.wbm_prefix + self.price_url)
                element = driver.find_element_by_xpath("//div[@id='wbMeta']/p[2]/strong")
                numberOfPriceSnapshots = int(re.sub("[^0-9]", "", element.text)) + 1

            return numberOfFeatureSnapshots + numberOfPriceSnapshots
        except Exception as e:
            print "__analyzeWBMSummaryPage %s" % e
            if driver is not None:
                driver.close()
                driver.quit()
            driver = webdriver.Chrome();
            return 0

    def successfulRate(self):
        self.expectedNumberOfLinks = self.__analyzeWBMSummaryPage()
        self.actualNumberOfLinks = self.db.getNumberOfFeatureSnapshots(self.itemID)\
                                   + self.db.getNumberOfPriceSnapshots(self.itemID);
    
        if self.expectedNumberOfLinks == 0 :
            self.successfulRate = -1.0
            return self.itemID, 0, 0, -1.0
        self.successfulRate = self.actualNumberOfLinks*1.0 / self.expectedNumberOfLinks
        return self.itemID, self.actualNumberOfLinks, \
               self.expectedNumberOfLinks, \
               self.actualNumberOfLinks*1.0 / self.expectedNumberOfLinks

if __name__ == '__main__':
    db = database()
    for itemID in range (1, 1130):
        crawlEvaluator = CrawlEvaluator(itemID)
        print crawlEvaluator.successfulRate()
        db.storeEvaluation(itemID, crawlEvaluator.successfulRate)
    driver.close()
    driver.quit()

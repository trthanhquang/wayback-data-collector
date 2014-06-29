import urllib2
from database import *
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

class CrawlEvaluator(object):
    wbm_prefix = "http://web.archive.org/web/*/"
    
    def __init__ (self, itemID):
        self.itemID = itemID

        ######CHANGE THIS IF NOT CRAWLING PRICE######
        url = database().getWebsitePriceURL(itemID)
        #############################################
        
        if not url.startswith("http"):
            self.url = "http://" + url
        else:
            self.url = url
        
    def __analyzeWBMSummaryPage (self):
        try: 
            driver = webdriver.Chrome();
            driver.get(self.wbm_prefix + self.url)
            element = driver.find_element_by_xpath("//div[@id='wbMeta']/p[2]/strong")
            keyword = element.text
            driver.close()
            driver.quit()
            return int(re.sub("[^0-9]", "", keyword))
        except (urllib2.URLError, NoSuchElementException) as e:
            driver.close()
            driver.quit()
            return 0

    def successfulRate(self):
        self.expectedNumberOfLinks = self.__analyzeWBMSummaryPage()
        self.actualNumberOfLinks = database().getNumberOfSnapshots(self.itemID);
    
        if self.expectedNumberOfLinks == 0 :
            return self.itemID, 0, 0, 1.0
        return self.itemID, self.actualNumberOfLinks, \
               self.expectedNumberOfLinks, \
               self.actualNumberOfLinks*1.0 / self.expectedNumberOfLinks

if __name__ == '__main__':
    crawlEvaluator = CrawlEvaluator(2264)
    print crawlEvaluator.successfulRate()

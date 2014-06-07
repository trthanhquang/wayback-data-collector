from bs4 import BeautifulSoup as BS
from selenium import webdriver

phantomJSpath = 'C:\phantomjs-1.9.7-windows\phantomjs.exe'
query = "http://www.bitdefender.com"

def main():
    driver = webdriver.PhantomJS(executable_path=phantomJSpath)
    driver.get(query)

    soup = BS(driver.page_source)
    driver.quit()

    f = open('pageSource.txt','w')
    f.write(soup.prettify().encode('utf8'))
    f.close()
    
if __name__ == "__main__":
    main()

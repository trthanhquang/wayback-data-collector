from crawl import *
from database import *
from htmlAnalyzer import *
import webbrowser

def openHTML(html,fileName = "temp.html"):
    f = open(fileName,'w')
    f.write(html.encode('utf8'))
    f.close()
    webbrowser.open(fileName)          
def openText(text,fileName = 'temp.txt'):
    f = open('temp.txt','w')
    f.write(text)
    f.close()
    webbrowser.open('temp.txt')

if __name__ == '__main__':
    db = database()
    html_list = db.getHTML(3681)

    initSearch = True
    searchString = ""
    (snapshot_date,html) = html_list[0]
    openHTML(html)
    searchString = str(raw_input('Enter search string: '))

    for (snapshot_date, html) in html_list:
        print snapshot_date
        analyzer = htmlAnalyzer(html)

        if(analyzer.searchText(searchString)==-1):
            print 'Unable to find: '+searchString
            print 'Suspect change in Content!'
            openHTML(html)
            openText(analyzer.getText())
            
            searchString = str(raw_input('Enter new search string: '))
            while (analyzer.searchText(searchString) == -1):
                print 'Unable to find: '+searchString          
                searchString = str(raw_input('Enter new search string: '))
        print 'OK'

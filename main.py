from waybackmachine import *

def main():
        m = WaybackMachine()
        dat = m.hasData("http://facebook.com")
        
        dat = m.testExtract("http://bitdefender.com")
        for t in dat:
                print t
        
if __name__ == "__main__":
        main()

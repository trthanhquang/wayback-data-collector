# ================================================================================
# Wayback Machine Endpoint Executor
# Developed by Tag Kim (Ph D.)
# This program is a data crawler designed to collect webpages in Wayback Machine.
# Visit http://web.archive.org to get more imformation.
#
# To run the program, you need to install drtag.web Python module.
# Send me an email: masan.korea@gmail.com
# All right reseved.
# ================================================================================
#Import parsers
from drtag.waybackmachine import *
import sys,os,glob
from colorconsole import terminal

screen = terminal.get_terminal()
screen.clear()
screen.gotoXY(0,0)

# --------------------------------------------------------------------------------
# --<CLASS>-----------------------------------------------------------------------
class MyMsg:
    menu = """1. Create Input File
2. Collect main pages yearly
3. Collect pages (1 level depth) from a data folder
4. Create a database schema
5. Map page data files onto a SQLite file
6. About the program
7. Exit"""
    menu_1 = """1. Check if your address exists
2. Create CSV input
3. Go back
4. Exit"""
    cursor = ">>> "
    sep = "/========================================================/\n"
    def show_start_msg(cls):
        screen.cprint(11,11,"/========================================================/\n\n")
        screen.cprint(14,0,"                  WAYBACK DATA COLLECTOR\n\n")
        screen.cprint(11,11,"/========================================================/\n\n")
        screen.cprint(10,0,"         Dr. Yuanyuan Chen and Dr. Taekyung Kim\n\n")
        screen.cprint(15,0,"          Information Systems School of Computing\n")
        screen.cprint(15,0,"            National University of Singapore\n\n")
        screen.cprint(7,0,"                Version 0.0.1 (2013)\n\n")
        screen.cprint(11,11,"/========================================================/\n")
        screen.reset()
    Show_start_msg = classmethod(show_start_msg)
# --------------------------------------------------------------------------------
# --<CLASS>-----------------------------------------------------------------------
class Menu_CreateInputFile:
    def __init__(self):
        while True:
            print MyMsg.menu_1
            make_sep_line()
            choice = int(raw_input(MyMsg.cursor))
            make_sep_line()
            if choice == 1: self.do_1()
            elif choice == 2: self.do_2()
            elif choice == 3:
                self.do_3()
                break
            else:
                self.do_4()
                sys.exit(1)
# --------------------------------------------------------------------------------
    def do_1(self):
        while True:
            try:
                machine = WaybackMachine()
                print "TYPE URL STARTS WITH HTTP"
                addr = raw_input(MyMsg.cursor)
                print "BE PATIENT. 10 SECONDS TO 1 MINUTES."
                if machine.hasData(addr):
                    print "Yes, the database has"
                else:
                    print "Sorry, the database does not have"
                make_sep_line()
                break
            except:
                if not try_again(): break
# --------------------------------------------------------------------------------
    def do_2(self):
        while True:
            try:
                toybox = ToyBoxInput()
                while True:
                    identifier = raw_input("Identifier >>>")
                    addr = raw_input("URL >>>")
                    syear = int(raw_input("Start year >>>"))
                    eyear = int(raw_input("End year >>>"))
                    toybox.makeInputSeq(identifier,addr,syear,eyear)
                    option = raw_input("Do you want to continue input? (Y/N) >>>")
                    if option.lower() == "n":
                        break
                    print "\n"
                if len(toybox.inputData) > 0:
                    file_path = raw_input("Input CSV output path >>>")
                    toybox.exportCsv(file_path)
                    print "The input file is created."
                del toybox
                break
            except:
                if not try_again(): break
    def do_3(self):
        return
    def do_4(self):
        sys.exit(0)
# --------------------------------------------------------------------------------
# --<CLASS>-----------------------------------------------------------------------
class Menu_CollectMain:
    def __init__(self):
        while True:
            try:
                outFolder = raw_input("Input output folder (X = going back)>>>")
                assert outFolder.lower() != 'x',""
                if not os.path.exists(outFolder):
                    os.mkdir(outFolder)
                inputFile = raw_input("Input data file path >>>")
                num_of_agent = int(raw_input("How many agents? (recommend = 8) >>>"))
                controller = WaybackController("input_log.log")
                controller.readInputFile(inputFile)
                print "\nWORKING NOW\n\n"
                controller.collectData(outFolder,num_of_agent)
                print "\n\nDONE\n"
                del controller
                break
            except:
               if not try_again(): break
# --------------------------------------------------------------------------------
# --<CLASS>-----------------------------------------------------------------------
class Menu_CollectPages:
    def __init__(self):
        while True:
            try:
                pickle_dir = raw_input("Input data file folder >>>")
                if not pickle_dir.endswith("/"):
                    pickle_dir += "/*.wayback"
                else:
                    pickle_dir += "*.wayback"
                files = glob.glob(pickle_dir)
                navCnt = NavigatorController()
                for file in files:
                    print "FILE: "+os.path.basename(file)
                    navCnt.read_pickle(file) #initializing master node
                    navCnt.extract_pages()
                    new_filename_list = list(os.path.splitext(file))
                    new_filename_list[-1] = ".waybackfull"
                    new_filename = "".join(new_filename_list)
                    print "\nSAVING..."
                    navCnt.export_pickle(new_filename)
                    print "\nDATA EXPORTED"
                print "All complted\n\n"
                break
            except:
                if not try_again(): break
# --------------------------------------------------------------------------------
# --<CLASS>-----------------------------------------------------------------------
class Menu_CreateSchema:
    def __init__(self):
        while True:
            try:
                db_file = raw_input("Database location >>>")
                tbs = ToyBoxSchema(db_file)
                tbs.create_schema()
                tbs.disconnect()
                print "\nDatabase schema is created.\n"
                break
            except:
                if not try_again(): break
# --------------------------------------------------------------------------------
# --<CLASS>-----------------------------------------------------------------------
class Menu_MapSqlite:
    def __init__(self):
        while True:
            try:
                db_file = raw_input("Database location >>>")
                pickle_dir = raw_input("Input data file folder >>>")
                if not pickle_dir.endswith("/"):
                    pickle_dir += "/*.waybackfull"
                else:
                    pickle_dir += "*.waybackfull"
                files = glob.glob(pickle_dir)
                tbwd = ToyBoxWriteDatabase(db_file)
                for file in files:
                    print "FILE: "+os.path.basename(file)
                    tbwd.read_pickle(file)
                    tbwd.update()
                print "All complete"
                break
            except:
                if not try_again(): break
# --------------------------------------------------------------------------------
# --<CLASS>-----------------------------------------------------------------------
class Menu_About:
    def about_me(cls):
        clear_screen()
        make_title("                      W E L C O M E                      ")
        print "This program collects webpages from Wayback Machine."
        print "You can learn about Wayback Machine from http://web.archive.org"
        print "First, you need to prepare an input file which is a comma separated value file consisting three elements: Identifier,URL and Year Code."
        print "For example, a file has a row, 'avg,http://www.avg.com,2013' That means you want to collect webpages published in 2013 from http://www.avg.com with identifying it as avg."
        print "You may refer a sample input file for further information."
        print "Next you have an anchor dataset which has a file extention, .wayback ."
        print "Using the anchor dataset, the program can collect webpages and make an object data file with file extension, .waybackfull ."
        print "Now you can import the object file into Python directly to analyze it, or you can build a sqlite3 database."
        print "You need to know that webpage source codes are compressed by ZLib which is a standard Python library."
        print "To learn about how to decode data, please read the technical guideline supplied with this program."
        print "\nThank you."
    About_me = classmethod(about_me)
# --------------------------------------------------------------------------------
def try_again():
    screen.set_color(12,0)
    exitor = raw_input("ERROR. TRY AGAIN?(Y), GOING BACK?(N) OR EXIT(X)? >>>")
    screen.reset()
    if exitor.lower() == "n":
        return False #going back
    elif exitor.lower() == "y":
        return True
    else:
        print "Bye."
        sys.exit(0)
# --------------------------------------------------------------------------------
def make_sep_line():
    screen.set_color(fg=8,bk=8)
    print MyMsg.sep
    screen.reset()

def make_title(title):
    screen.set_color(fg=0,bk=14)
    print title
    screen.reset()

def clear_screen():
    screen.clear()
    screen.gotoXY(0,0)
# --------------------------------------------------------------------------------
def main():
    MyMsg.Show_start_msg()
    make_sep_line()
    while True:
        print MyMsg.menu
        print ""
        selected = int(raw_input(MyMsg.cursor))
        make_sep_line()
        if selected == 1:
            clear_screen()
            make_title("CREATE INPUT FILE")
            mnu1 = Menu_CreateInputFile()
        elif selected == 2:
            clear_screen()
            make_title("MAIN PAGE COLLECTION - ANCHOR DATASET")
            mnu2 = Menu_CollectMain()
        elif selected == 3:
            clear_screen()
            make_title("CRAWLING ARCHIVED WEBPAGES")
            mnu3 = Menu_CollectPages()
        elif selected == 4:
            clear_screen()
            make_title("CREATE SQLITE3 DATABASE SCHEMA")
            mnu4 = Menu_CreateSchema()
        elif selected == 5:
            clear_screen()
            make_title("MAPPING OBJECT DATA INTO DATABASE")
            mnu5 = Menu_MapSqlite()
        elif selected == 6:
            Menu_About.About_me()
        else:
            print "Bye."
            sys.exit(0)
        raw_input("Continue to press any key...")
        clear_screen()
# --------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
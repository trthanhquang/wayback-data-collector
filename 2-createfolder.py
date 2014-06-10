# ================================================================================
# Creates
# folder based on publisher name
# sub folder based on product name 
# ================================================================================
import os
import csv

path = './data/'
with open('combinedlist.csv', 'rb') as infile:
    reader = csv.DictReader(infile)
    for row in reader:
        publishername = row['publisher_name']
        productname = row['app_name']
        productname = productname.replace(':', '-')
        dir = path + publishername
        subdir = path + publishername + '/' + productname
        if os.path.exists(dir):
            if not os.path.exists(subdir):
                os.makedirs(subdir)
        else:
            os.makedirs(dir)
            if not os.path.exists(subdir):
                os.makedirs(subdir)




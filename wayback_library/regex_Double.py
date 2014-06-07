import re

def main() :
    number = "adsfasdf0.50a.52sdfas"   #any string

    #regex to determine if string contains any (float) number
    match = re.finditer("[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?", number)
    for m in match:
        print m.start(), m.end(), m.group(0)

if (__name__ == "__main__") :
    main()

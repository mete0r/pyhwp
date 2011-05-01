import hwp50, sys

if __name__=='__main__':
    hwpdoc = hwp50.Document(sys.argv[1])
    print hwpdoc.header.version

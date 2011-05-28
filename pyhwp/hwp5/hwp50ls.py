import hwp50
import sys

doc = hwp50.Document(sys.argv[1])
for n in doc.streamNames():
    print n

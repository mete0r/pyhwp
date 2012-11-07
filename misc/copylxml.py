import sys
import os.path
import shutil

try:
    import lxml
except ImportError:
    print 'no lxml found'
    sys.exit(0)

if sys.platform != 'win32':
    sys.exit(os.system('pip install lxml'))

lxml_path = os.path.dirname(lxml.__file__)
dest_path = os.path.join(sys.argv[1], 'lxml')
shutil.copytree(lxml_path, dest_path)

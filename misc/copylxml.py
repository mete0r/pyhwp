import sys
import os.path
import shutil

def main():
    if sys.platform == 'win32':
        try:
            import lxml
        except ImportError:
            print 'no lxml found'
        else:
            lxml_path = os.path.dirname(lxml.__file__)
            dest_path = os.path.join(sys.argv[1], 'lxml')
            shutil.copytree(lxml_path, dest_path)
        sys.exit(0)
    else:
        sys.exit(os.system('pip install lxml'))


if __name__ == '__main__':
    main()

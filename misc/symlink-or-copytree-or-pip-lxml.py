import sys
import os.path
import shutil

def main():
    src_path = os.path.join(sys.argv[1], 'lxml')
    dst_path = os.path.join(sys.argv[2], 'lxml')
    print 'lxml src:', src_path
    print 'lxml dst:', dst_path
    if sys.platform == 'win32':
        if os.path.exists(src_path):
            print 'lxml: copytree-ing...'
            shutil.copytree(src_path, dst_path)
        else:
            print 'lxml: not found. skipping...'
        sys.exit(0)
    else:
        if os.path.exists(src_path):
            print 'lxml: symlinking...'
            os.symlink(src_path, dst_path)
            sys.exit(0)
        else:
            print 'lxml: installing...'
            sys.exit(os.system('pip install lxml'))


if __name__ == '__main__':
    main()

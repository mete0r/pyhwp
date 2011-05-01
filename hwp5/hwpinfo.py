from .filestructure import File
import sys

def main():
    args = list(sys.argv[1:])

    try:
        filename = args.pop(0)
    except IndexError:
        print 'filename required'
        return -1

    hwpfile = File(filename)

    available_components = ['summaryinfo', 'previewtext', 'previewimage', 'bindata']

    try:
        component = args.pop(0)
    except IndexError:
        for name in hwpfile.list_streams():
            print name
        print ''
        print 'compoenents:'
        print '\t' + ' | '.join(available_components)
        return 0

    if not component in available_components:
        print 'compoenents:'
        print '\t' + ' | '.join(available_components)
        return -1;

    if component == 'summaryinfo':
        print hwpfile.summaryinfo
    elif component == 'previewtext':
        print hwpfile.previewtext
    elif component == 'previewimage':
        sys.stdout.write( hwpfile.previewimage )
    elif component == 'bindata':
        try:
            bindataname = args.pop(0)
        except IndexError:
            print 'bindata name is required'
            return -1;
        sys.stdout.write( hwpfile.read_bindata(bindataname) )
    else:
        print 'unknown component'
        return -1

if __name__ == '__main__':
    main()

import sys

class ArgError(Exception):
    pass

class OptionParser(object):
    def __init__(self, *args, **kwargs):
        from optparse import OptionParser, make_option
        self.op = OptionParser(*args, **kwargs)

        self.op.add_option('--loglevel', dest='loglevel', default='warning', help='loglevel (debug, info, warning, error, critical)')
        self.op.add_option('-o', '--outfile', dest='outfile', default='-', help='output filename (default: standard output')

    def add_option(self, *args, **kwargs):
        self.op.add_option(*args, **kwargs)

    def parse_args(self, *args, **kwargs):
        options, args = self.op.parse_args(*args, **kwargs)
        options = self.post_parse_options(options)
        args = self.post_parse_args(args)
        return options, args

    def post_parse_options(self, options):
        import logging, sys
        from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL
        loglevels = dict(debug=DEBUG, info=INFO, warning=WARNING, error=ERROR, critical=CRITICAL)
        options.loglevel = loglevels[options.loglevel]

        if options.outfile == '-':
            options.outfile = sys.stdout
        else:
            options.outfile = file(options.outfile, 'w')
        return options

    def post_parse_args(self, args):
        return args

    def print_help(self):
        return self.op.print_help()

import logging
logformat_xml = logging.Formatter('<!-- %(levelname)8s: %(message)s -->')
logformat_plain = logging.Formatter('%(levelname)8s: %(message)s')
def loghandler(out, formatter):
    handler = logging.StreamHandler(out)
    handler.setFormatter(formatter)
    return handler

def getlogger(options, handler=None):
    import sys
    if handler is None:
        handler = loghandler(sys.stderr, logformat_plain)

    logger = logging.getLogger('hwp5')
    logger.setLevel(options.loglevel)
    logger.addHandler(handler)
    return logger

def args_pop(args, name):
    try:
        return args.pop(0)
    except IndexError:
        raise ArgError, name+' is required'

def args_pop_range(args):
    if len(args) > 0:
        range = args.pop(0)
        range = range.split(':', 1)
        if len(range) == 1:
            start = int(range[0])
            end = start + 1
        else:
            start, end = range

            if start != '':
                start = int(start)
            else:
                start = 0

            if end != '':
                end = int(end)
            else:
                end = None
        return (start, end)

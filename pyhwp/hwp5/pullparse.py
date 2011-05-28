from .recordstream import read_records

STARTREC = 0
ENDREC = 2
def pullparse_records(records):
    stack = []
    for rec in records:
        level = rec.level

        while level < len(stack):
            yield ENDREC, stack.pop()
        while len(stack) < level:
            raise Exception('invalid level: Record %d, level %d, expected level=%d'%(rec.seqno, level, len(stack)))
        assert(len(stack) == level)

        if len(stack) > 0:
            stack[-1].subrecs.append(rec)
        stack.append(rec)
        yield STARTREC, rec

    while 0 < len(stack):
        yield ENDREC, stack.pop()

def pullparse(f):
    return pullparse_records(read_records(f))

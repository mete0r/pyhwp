
class SubStream:
    def __init__(self, basestream, size):
        self.basestream = basestream
        self.size = size
        self.pos = 0
        self.buflist = []
    def read(self, n=-1):
        if self.basestream is None:
            return ''
        if n < 0:
            n = self.size - self.pos
        if self.size < self.pos + n:
            n = self.size - self.pos
        if n > 0:
            data = self.basestream.read(n)
            assert(len(data) == n)
            self.buflist.append(data)
            self.pos += n
        else:
            data = ''
        if self.pos >= self.size:
            self.basestream = None
        return data
    def close(self):
        self.read()
        self.basestream = None
    def is_closed(self):
        return self.basestream is None
    def reopen(self):
        from cStringIO import StringIO
        self.basestream = StringIO(''.join(self.buflist))

class BufStream:
    def __init__(self, basestream):
        self.basestream = basestream
        self.buflist = []
        self.bytes = None
    def read(self, n=-1):
        if n == -1:
            data = self.basestream.read(self)
        else:
            data = self.basestream.read(self, n)
        if data != '':
            self.buflist.append(data)
        else:
            self.basestream = None
        return data
    def close(self):
        self.basestream = None
    def getbytes(self):
        if self.bytes is None:
            self.bytes = ''.join(self.buflist)
        return self.bytes

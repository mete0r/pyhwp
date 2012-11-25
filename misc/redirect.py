from __future__ import with_statement
import subprocess
import sys

if __name__ == '__main__':
    with file(sys.argv[1], 'wb') as f:
        p = subprocess.Popen(sys.argv[2:], stdout=f)
        p.wait()
        raise SystemExit(p.returncode)

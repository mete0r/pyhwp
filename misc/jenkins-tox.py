# -*- coding: utf-8 -*-

if __name__ == '__main__':
    import os
    import os.path
    buildout = os.path.join('bin', 'buildout')
    tox = os.path.join('bin', 'tox')
    if not os.path.exists(buildout):
        execfile('bootstrap.py')
    if os.system(buildout):
        raise SystemExit(1)
    if os.system(tox):
        raise SystemExit(1)

    from subprocess import Popen
    pep8out = file('pep8.out', 'w')
    try:
        pep8 = os.path.join('bin', 'pep8')
        sources = os.path.join('pyhwp', 'hwp5')
        p = Popen([pep8, sources], stdout=pep8out)
        p.wait()
    finally:
        pep8out.close()

    raise SystemExit(0)

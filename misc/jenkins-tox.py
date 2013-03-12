# -*- coding: utf-8 -*-
import sys

if __name__ == '__main__':
    import os
    import os.path
    buildout = os.path.join('bin', 'buildout')
    tox = os.path.join('bin', 'tox')
    if sys.platform == 'win32':
        buildout += '.exe'
        tox += '.exe'
    force_exec_bootstrap = ('EXEC_BOOTSTRAP_PY' in os.environ and
                            os.environ['EXEC_BOOTSTRAP_PY'] == 'true')
    if not os.path.exists(buildout) or force_exec_bootstrap:
        execfile('bootstrap.py')
    if os.system(buildout):
        raise SystemExit(1)
    if os.path.exists('MANIFEST'):
        os.unlink('MANIFEST')

    coverage = os.path.join('bin', 'coverage')
    os.system(coverage + ' erase')

    if os.system(tox):
        raise SystemExit(1)

    os.system(coverage + ' combine')
    os.system(coverage + ' xml -i -o coverage-original.xml --include="*hwp5*","*unokit*"')
    os.system(' '.join([sys.executable,
                        os.path.join('misc', 'fix-coverage.py'),
                        'coverage-original.xml',
                        'coverage.xml']))

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

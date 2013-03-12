setuptools_python = System.getenv("SETUPTOOLS_PYTHON")
if (setuptools_python == null) {
    setuptools_python = "python"
}

runtime = Runtime.getRuntime()

def shellexec(cmd) {
    println "executing " + cmd
    proc = runtime.exec(cmd)
    stdout = proc.getInputStream()
    stderr = proc.getErrorStream()
    def pump_stdout = Thread.start {
        buf = new byte[4096]
        while (true) {
            len = stdout.read(buf)
            if (len == -1) {
                return
            }
            System.out.write(buf, 0, len)
            System.out.flush()
        }
    }
    def pump_stderr = Thread.start {
        buf = new byte[4096]
        while (true) {
            len = stderr.read(buf)
            if (len == -1) {
                return
            }
            System.err.write(buf, 0, len)
        }
    }
    retcode = proc.waitFor()
    println "ret = " + retcode
    return retcode
}

def cmd = setuptools_python + " " + "misc" + File.separator + "jenkins-tox.py"
retcode = shellexec(cmd)
System.exit(retcode)

import os
import os.path
cwd = os.getcwd()
os.chdir(os.path.dirname(__file__))
try:
    from setuptools import setup, find_packages
    setup(name='oxt.tool',
          install_requires=['docopt', 'unokit', 'discover'],
          packages=find_packages(),
          entry_points = {
              'console_scripts': [
                  'run-in-lo = oxt_tool:run_in_lo',
                  'oxt-storage-ls = oxt_tool.storage:ls_main',
                  'oxt-storage-put = oxt_tool.storage:put_main',
                  'oxt-storage-get = oxt_tool.storage:get_main',
                  'oxt-manifest-init = oxt_tool.manifest:init_main',
                  'oxt-manifest-ls = oxt_tool.manifest:ls_main',
                  'oxt-manifest-add = oxt_tool.manifest:add_main',
                  'oxt-manifest-rm = oxt_tool.manifest:rm_main',
                  'oxt-desc-init = oxt_tool.description:init_main',
                  'oxt-desc-show = oxt_tool.description:show_main',
                  'oxt-desc-version = oxt_tool.description:version_main',
                  'oxt-desc-ls = oxt_tool.description:ls_main',
                  'oxt-pkg-init = oxt_tool.package:init_main',
                  'oxt-pkg-show = oxt_tool.package:show_main',
                  'oxt-pkg-build = oxt_tool.package:build_main',
                  'oxt-pkg-check = oxt_tool.package:check_main',
              ],
              'zc.buildout': [
                  'installer = oxt_tool:Installer'
                  ,'console = oxt_tool:Console'
                  ,'test = oxt_tool:TestRunner'
              ]
          })
finally:
    os.chdir(cwd)

OXTPKG=pyhwp.oxt
UNOPKG=unopkg
SOFFICE=soffice

SRC=description.xml pyhwp.py Types.xcu Filter.xcu META-INF/manifest.xml registration/COPYING.txt description/*.txt

$(OXTPKG): $(SRC)
	-mkdir pythonpath
	cd ../pyhwp; PYTHONPATH=../oxt/pythonpath python setup.py install --no-compile --install-lib=../oxt/pythonpath --install-data=../oxt/pythonpath --install-scripts=../oxt/bin --single-version-externally-managed --record=../oxt/pyhwp.egg.record
	zip -9 -r $@ $(SRC) pythonpath

validate: $(OXTPKG)
	$(UNOPKG) validate -v $(OXTPKG)

install: $(OXTPKG)
	$(UNOPKG) add -v $(OXTPKG)

uninstall:
	$(UNOPKG) remove -f $(OXTPKG)

reinstall: uninstall install

runserver:
	PYTHONPATH=../pyhwp soffice "-accept=socket,host=localhost,port=2002;urp;"

.PHONY: validate install uninstall runserver

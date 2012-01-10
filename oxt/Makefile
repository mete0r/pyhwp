OXTPKG=pyhwp.oxt
UNOPKG=/home/mete0r/prj/libreoffice/solver/unxlngi6.pro/installation/opt/program/unopkg
SOFFICE=/home/mete0r/prj/libreoffice/solver/unxlngi6.pro/installation/opt/program/soffice

SRC=description.xml pyhwp.py Addons.xcu Types.xcu Filter.xcu META-INF/manifest.xml #pythonpath.zip

$(OXTPKG): $(SRC)
	zip -9 $@ $(SRC)

validate: $(OXTPKG)
	$(UNOPKG) validate -v $(OXTPKG)

install: $(OXTPKG)
	$(UNOPKG) add -v $(OXTPKG)

uninstall:
	$(UNOPKG) remove -f $(OXTPKG)

reinstall: uninstall install

pythonpath.zip: utils.py
	zip -0 pythonpath.zip utils.py
	#cd ../pyhwp; zip -0 -r ../oxt/pythonpath.zip hwp5

runserver:
	PYTHONPATH=../pyhwp soffice "-accept=socket,host=localhost,port=2002;urp;"

.PHONY: validate install uninstall runserver

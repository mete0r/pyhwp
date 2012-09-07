OXTPKG=hwp5.oxt
UNOPKG=unopkg
SOFFICE=soffice

SRC=description.xml components.py Types.xcu Filter.xcu META-INF/manifest.xml registration/COPYING.txt description/*.txt

$(OXTPKG): $(SRC)
	zip -9 -r $@ $(SRC) pythonpath

validate: $(OXTPKG)
	$(UNOPKG) validate -v $(OXTPKG)

install: $(OXTPKG)
	$(UNOPKG) add -v -s $(OXTPKG)

uninstall:
	$(UNOPKG) remove -f $(OXTPKG)

reinstall: uninstall install

clean:
	$(RM) $(OXTPKG)

runserver:
	PYTHONPATH=../pyhwp soffice "-accept=socket,host=localhost,port=2002;urp;"

.PHONY: validate install uninstall runserver clean

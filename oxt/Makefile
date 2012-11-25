OXTPKG:=../dist/hwp5-$(shell git describe --dirty).oxt
UNOPKG=unopkg

$(OXTPKG):
	../bin/oxt-build

validate: $(OXTPKG)
	$(UNOPKG) validate -v hwp5.oxt

install: $(OXTPKG)
	$(UNOPKG) add -v -s $(OXTPKG)

uninstall:
	$(UNOPKG) remove -f hwp5.oxt

reinstall: uninstall install

clean:
	$(RM) $(OXTPKG)

.PHONY: validate install uninstall clean

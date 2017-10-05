define ALL
	update-requirements
	install-jython
endef
ALL:=$(shell echo $(ALL))  # to remove line-feeds

define REQUIREMENTS_FILES
	requirements/dev.txt
	requirements/lint.txt
	requirements/test.txt
	requirements.txt
endef
REQUIREMENTS_FILES:=$(shell echo $(REQUIREMENTS_FILES))

define REQUIREMENTS_IN
	requirements.in
endef
REQUIREMENTS_IN:=$(shell echo $(REQUIREMENTS_IN))

define REQUIREMENTS_IN_TEST
	requirements/test.in
	requirements.in
endef
REQUIREMENTS_IN_TEST:=$(shell echo $(REQUIREMENTS_IN_TEST))

define REQUIREMENTS_IN_LINT
	requirements/lint.in
endef
REQUIREMENTS_IN_LINT:=$(shell echo $(REQUIREMENTS_IN_LINT))

define REQUIREMENTS_IN_DEV
	requirements/dev.in
	requirements/lint.in
	requirements/test.in
	requirements.in
endef
REQUIREMENTS_IN_DEV:=$(shell echo $(REQUIREMENTS_IN_DEV))

offline?=0

ifeq (1,$(offline))
PIP_NO_INDEX:=--no-index
endif

FIND_LINKS?=
VENV	:= . bin/activate &&


.PHONY: all
all: $(ALL)

.PHONY: bootstrap
bootstrap:
	[ -e bin/activate ] || virtualenv -p python2.7 .
	$(VENV) pip install -U setuptools pip wheel pip-tools
	make update-requirements
	$(VENV) buildout

.PHONY: update-requirements
update-requirements: $(REQUIREMENTS_FILES)
	$(VENV) pip-sync $(FIND_LINKS) $(PIP_NO_INDEX) requirements/dev.txt

requirements.txt: $(REQUIREMENTS_IN)
	$(VENV)	pip-compile $(FIND_LINKS) $(PIP_NO_INDEX) $(pip-compile-options) -o $@ $^

requirements/test.txt: $(REQUIREMENTS_IN_TEST)
	$(VENV) pip-compile $(FIND_LINKS) $(PIP_NO_INDEX) $(pip-compile-options) -o $@ $^

requirements/lint.txt: $(REQUIREMENTS_IN_LINT)
	$(VENV) pip-compile $(FIND_LINKS) $(PIP_NO_INDEX) $(pip-compile-options) -o $@ $^

requirements/dev.txt: $(REQUIREMENTS_IN_DEV)
	$(VENV) pip-compile $(FIND_LINKS) $(PIP_NO_INDEX) $(pip-compile-options) -o $@ $^


.PHONY: notebook
notebook:
	$(VENV)	jupyter notebook --notebook-dir=notebooks


.PHONY: clitest
clitest:
	$(VENV) env SAMPLES=samples clitest -1 --prefix 3 pyhwp-tests/cli_tests/hwp5proc.txt pyhwp-tests/cli_tests/hwp5odt.txt


.PHONY: install-jython
install-jython: parts/jython2.7/bin/jython
parts/jython2.7/bin/jython:
	rm -rf parts/jython2.7
	mkdir -p parts
	$(VIRTUAL_ENV)/bin/jip install org.python:jython-installer:2.7.1
	java -jar $(VIRTUAL_ENV)/javalib/jython-installer-2.7.1.jar -s -d $(PWD)/parts/jython2.7

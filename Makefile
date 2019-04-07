define ALL
	update-requirements
	install-jython
endef
ALL:=$(shell echo $(ALL))  # to remove line-feeds

define REQUIREMENTS_FILES
	requirements/dev.txt
	requirements/docs.txt
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

define REQUIREMENTS_IN_DOCS
	requirements/docs.in
endef
REQUIREMENTS_IN_DOCS:=$(shell echo $(REQUIREMENTS_IN_DOCS))

define REQUIREMENTS_IN_DEV
	requirements/dev.in
	requirements/docs.in
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

requirements/docs.txt: $(REQUIREMENTS_IN_DOCS)
	$(VENV) pip-compile $(FIND_LINKS) $(PIP_NO_INDEX) $(pip-compile-options) -o $@ $^

requirements/dev.txt: $(REQUIREMENTS_IN_DEV)
	$(VENV) pip-compile $(FIND_LINKS) $(PIP_NO_INDEX) $(pip-compile-options) -o $@ $^


.PHONY: extract-messages
extract-messages:
	$(VENV) python setup.py extract_messages --input-paths=pyhwp/hwp5/proc --output-file=pyhwp/hwp5/locale/hwp5proc.pot
	$(VENV) python setup.py extract_messages --input-paths=pyhwp/hwp5/hwp5html.py --output-file=pyhwp/hwp5/locale/hwp5html.pot
	$(VENV) python setup.py extract_messages --input-paths=pyhwp/hwp5/hwp5odt.py --output-file=pyhwp/hwp5/locale/hwp5odt.pot
	$(VENV) python setup.py extract_messages --input-paths=pyhwp/hwp5/hwp5txt.py --output-file=pyhwp/hwp5/locale/hwp5txt.pot
	$(VENV) python setup.py extract_messages --input-paths=pyhwp/hwp5/hwp5view.py --output-file=pyhwp/hwp5/locale/hwp5view.pot

.PHONY: init-catalog
init-catalog:
	$(VENV) python setup.py init_catalog --domain=hwp5proc --input-file=pyhwp/hwp5/locale/hwp5proc.pot --locale=ko
	$(VENV) python setup.py init_catalog --domain=hwp5html --input-file=pyhwp/hwp5/locale/hwp5html.pot --locale=ko
	$(VENV) python setup.py init_catalog --domain=hwp5odt --input-file=pyhwp/hwp5/locale/hwp5odt.pot --locale=ko
	$(VENV) python setup.py init_catalog --domain=hwp5txt --input-file=pyhwp/hwp5/locale/hwp5txt.pot --locale=ko
	$(VENV) python setup.py init_catalog --domain=hwp5view --input-file=pyhwp/hwp5/locale/hwp5view.pot --locale=ko

.PHONY: update-catalog
update-catalog:
	$(VENV) python setup.py update_catalog --domain=hwp5proc --input-file=pyhwp/hwp5/locale/hwp5proc.pot
	$(VENV) python setup.py update_catalog --domain=hwp5html --input-file=pyhwp/hwp5/locale/hwp5html.pot
	$(VENV) python setup.py update_catalog --domain=hwp5odt --input-file=pyhwp/hwp5/locale/hwp5odt.pot
	$(VENV) python setup.py update_catalog --domain=hwp5txt --input-file=pyhwp/hwp5/locale/hwp5txt.pot
	$(VENV) python setup.py update_catalog --domain=hwp5view --input-file=pyhwp/hwp5/locale/hwp5view.pot

.PHONY: compile-catalog
compile-catalog:
	$(VENV) python setup.py compile_catalog --domain=hwp5proc
	$(VENV) python setup.py compile_catalog --domain=hwp5html
	$(VENV) python setup.py compile_catalog --domain=hwp5odt
	$(VENV) python setup.py compile_catalog --domain=hwp5txt
	$(VENV) python setup.py compile_catalog --domain=hwp5view

.PHONY: notebook
notebook:
	$(VENV)	jupyter notebook --notebook-dir=notebooks


.PHONY: test
test:
	$(VENV) tox --parallel 8 -e py27,py34,py35,py36,py37,pypy,pypy3

.PHONY: test-report
test-report:
	$(VENV) coverage combine .tox/*/tmp
	$(VENV) coverage report
	$(VENV) coverage html
	$(VENV) coverage xml

.PHONY: clitest
clitest:
	$(VENV) env LANG=C clitest -1 --prefix 3 pyhwp-tests/cli_tests/hwp5proc.txt pyhwp-tests/cli_tests/hwp5odt.txt pyhwp-tests/cli_tests/hwp5html.txt pyhwp-tests/cli_tests/hwp5txt.txt


.PHONY: install-jython
install-jython: parts/jython2.7/bin/jython
parts/jython2.7/bin/jython:
	rm -rf parts/jython2.7
	mkdir -p parts
	$(VIRTUAL_ENV)/bin/jip install org.python:jython-installer:2.7.1
	java -jar $(VIRTUAL_ENV)/javalib/jython-installer-2.7.1.jar -s -d $(PWD)/parts/jython2.7

BUILDOUT_DIR := ${realpath ../..}
JXML_DIR := ${realpath ..}
JXML_BIN_DIR:=$(JXML_DIR)/bin
JXML_LXML_DIR := ${JXML_DIR}/lxml
TEST_XSL_DIR := ${JXML_DIR}/tests/test-xsl
XML_FIXT_DIR := ${TEST_XSL_DIR}/fxt
TEST_GEN_DIR := ${TEST_XSL_DIR}/gen



XALAN_J_ARCHIVE = ${BUILDOUT_DIR}/parts/xalan-j_2_7_1-bin-2jars.tar.gz
XALAN_J_DIR = ${BUILDOUT_DIR}/parts/xalan-j_2_7_1
XALAN_J_CLASSPATH = ${XALAN_J_DIR}/xalan.jar:${XALAN_J_DIR}/xercesImpl.jar:${XALAN_J_DIR}/serializer.jar:${XALAN_J_DIR}/xml-apis.jar
XALAN_J_SYS_PROPS = -Djavax.xml.transform.TransformerFactory=org.apache.xalan.processor.TransformerFactoryImpl -Djavax.xml.parsers.DocumentBuilderFactory=org.apache.xerces.jaxp.DocumentBuilderFactoryImpl -Djavax.xml.parsers.SAXParserFactory=org.apache.xerces.jaxp.SAXParserFactoryImpl
XALAN_J_ENVSET = CLASSPATH=${XALAN_J_CLASSPATH}
XALAN_J_JYTHON = ${XALAN_J_ENVSET} ${JXML_BIN_DIR}/jython ${XALAN_J_SYS_PROPS}


DEFAULT_JYTHON = ${JXML_BIN_DIR}/jython
JXML_ENVSET = JYTHONPATH=${JXML_DIR}:${JXML_LXML_DIR}

.PHONY: test-jaxp test-jaxp-xalan test-python test-jython test-jython-xalan test-xsl test-xsl-xalan
all: test-jaxp test-jaxp-xalan test-python test-jython test-jython-xalan test-xsl test-xsl-xalan

test-python:
	python test_lxml.py
test-jython:
	${JXML_ENVSET} ${DEFAULT_JYTHON} test_lxml.py
test-jython-xalan: ${XALAN_J_DIR}
	#${XALAN_J_JYTHON} test_textout.py
	${JXML_ENVSET} ${XALAN_J_JYTHON} test_lxml.py
test-xsl:
	for fn in `ls ${BUILDOUT_DIR}/test-xsl/gen/*.py`; do echo $$fn; ${JXML_ENVSET} ${DEFAULT_JYTHON} $$fn; done
test-xsl-xalan: ${XALAN_J_DIR}
	for fn in `ls ${BUILDOUT_DIR}/test-xsl/gen/*.py`; do echo $$fn; ${JXML_ENVSET} ${XALAN_J_JYTHON} $$fn; done
test-jaxp:
	${DEFAULT_JYTHON} test_jaxp.py
test-jaxp-xalan:
	${XALAN_J_JYTHON} test_jaxp.py



${XALAN_J_DIR}: ${XALAN_J_ARCHIVE}
	${BUILDOUT_DIR}/bin/pyhwp-unpack $< $@

${XALAN_J_ARCHIVE}:
	${BUILDOUT_DIR}/bin/pyhwp-download http://mirror.apache-kr.org/xalan/xalan-j/binaries/xalan-j_2_7_1-bin-2jars.tar.gz ${BUILDOUT_DIR}/parts 3ccda39bcd08b780436dfd2f22fb23d5

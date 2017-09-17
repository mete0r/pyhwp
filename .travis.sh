#!/bin/bash
case "$TRAVIS_PYTHON_VERSION" in
	"2.7")
		tox -e py27
		;;
	"pypy")
		tox -e pypy
		;;
esac

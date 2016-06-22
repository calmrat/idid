# Prepare variables
TMP = $(CURDIR)/tmp
VERSION = $(shell grep ^Version idid.spec | sed 's/.* //')
PACKAGE = idid-$(VERSION)
FILES = LICENSE README.rst \
		Makefile idid.spec \
		examples idid bin
ifndef USERNAME
    USERNAME = echo $$USER
endif


# Define special targets
all: docs packages
.PHONY: docs hooks

# Temporary directory
tmp:
	mkdir $(TMP)

# Run the test suite, optionally with coverage
test: tmp
	IDID_DIR=$(TMP) py.test tests -s
smoke: tmp
	IDID_DIR=$(TMP) py.test tests/test_cli.py
coverage: tmp
	IDID_DIR=$(TMP) coverage run --source=idid,bin -m py.test tests
	coverage report
	coverage annotate


# Build documentation, prepare man page
docs: man
	cd docs && make html
man: source
	cp docs/header.txt $(TMP)/man.rst
	tail -n+7 README.rst | sed '/^Status/,$$d' >> $(TMP)/man.rst
	rst2man $(TMP)/man.rst | gzip > $(TMP)/$(PACKAGE)/idid.1.gz


# RPM packaging
source:
	mkdir -p $(TMP)/{SOURCES,$(PACKAGE)}
	cp -a $(FILES) $(TMP)/$(PACKAGE)
	rm -rf $(TMP)/$(PACKAGE)/examples/mr.bob
tarball: source man
	cd $(TMP) && tar cfj SOURCES/$(PACKAGE).tar.bz2 $(PACKAGE)
rpm: tarball
	rpmbuild --define '_topdir $(TMP)' -bb idid.spec
srpm: tarball
	rpmbuild --define '_topdir $(TMP)' -bs idid.spec
packages: rpm srpm


# Python packaging
wheel:
	python setup.py bdist_wheel
upload:
	twine upload dist/*.whl


# Git hooks, vim tags and cleanup
hooks:
	ln -snf ../../hooks/pre-commit .git/hooks
	ln -snf ../../hooks/commit-msg .git/hooks
tags:
	find idid -name '*.py' | xargs ctags --python-kinds=-i
clean:
	rm -rf $(TMP) build dist idid.egg-info
	find . -type f -name "*.py[co]" -delete
	find . -type f -name "*,cover" -delete
	find . -type d -name "__pycache__" -delete
	cd docs && make clean
	rm -f .coverage tags

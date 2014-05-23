PYTHON = $(shell which python 2.7)
ENV = $(CURDIR)/env

virtual-env:
	virtualenv --python=$(PYTHON) $(ENV)

test-env: virtual-env
	$(ENV)/bin/pip install -r requirements/test.txt

env: virtual-env
	$(ENV)/bin/pip install -r requirements/base.txt

run: env
	$(ENV)/bin/python tagsana/app_tagsana.py

run-tests: test-env
	$(ENV)/bin/nosetests ./tagsana/ -vs --with-coverage --cover-package=tagsana.tagsana,tagsana.app_tagsana

clean:
	rm -rf $(ENV)

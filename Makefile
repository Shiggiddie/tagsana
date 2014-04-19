PYTHON = $(shell which python 2.7)
ENV = $(CURDIR)/env

virtual-env:
	virtualenv --python=$(PYTHON) $(ENV)

env: virtual-env
	$(ENV)/bin/pip install -r requirements/base.txt

run: env
	$(ENV)/bin/python dental_flask_app/dental_flask_app.py

clean:
	rm -rf $(ENV)

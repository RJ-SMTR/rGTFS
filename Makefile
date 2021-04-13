.PHONY: create-env update-env

REPO=$(shell basename $(CURDIR))

create-env:
	python3 -m venv .$(REPO);


install-env:
	. .$(REPO)/bin/activate; \
			pip install -U pip \
			pip3 install --upgrade  -r requirements-dev.txt; \
			python setup.py develop;

update-env:
	. .$(REPO)/bin/activate; \
	pip install -U pip \
	pip3 install --upgrade -r requirements-dev.txt;

attach-kernel:
	. .$(REPO)/bin/activate; python3 -m ipykernel install --user --name=$(REPO);

setup-workspace:
	mkdir data

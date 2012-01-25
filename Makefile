all: develop
	
develop:
	python setup.py develop

install:
	python setup.py install

test:
	nosetests
	

package=conf_tools

include pypackage.mk

bump-upload:
	bumpversion patch
	python setup.py sdist upload


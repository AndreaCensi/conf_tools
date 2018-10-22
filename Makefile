package=conf_tools

include pypackage.mk

bump-upload:
	# bumpversion patch
	# python setup.py sdist upload
	bumpversion patch
	git push --tags
	git push --all
	rm -f dist/*
	python setup.py sdist
	twine upload dist/*
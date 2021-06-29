
all : readme docs

readme : README.ipynb 
	python -m jupyter nbconvert README.ipynb --execute --to markdown --output README.md

.PHONY: docs
docs : 
	python -m jupyter nbconvert README.ipynb --execute --to rst --output README.rst
	-sphinx-build docs _docs

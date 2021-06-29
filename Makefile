
all : readme docs

readme : README.ipynb 
	python3 -m jupyter nbconvert README.ipynb --execute --to markdown --output README.md

.PHONY: docs
docs : 
	python3 -m jupyter nbconvert README.ipynb --execute --to rst --output README.rst
	-sphinx-build docs _docs

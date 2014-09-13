all: clean
	mkdir dist
	python ./scripts/wheels2dmg scipy-stack 1.0 \
	    numpy scipy matplotlib ipython[notebook] \
	    --get-pip-url=${HOME}/Downloads/get-pip.py \
	    --dmg-out-dir=dist \
	    --dmg-build-dir=tmp \
	    --scratch-dir=scratch

clean:
	rm -rf dist tmp scratch

install:
	- sudo pip uninstall -y numpy scipy matplotlib ipython[notebook]
	hdiutil attach dist/scipy-stack-py27-1.0.dmg
	sudo installer -pkg /Volumes/scipy-stack-py27-1.0/scipy-stack-py27-1.0.pkg \
	    -verbose -target /
	hdiutil detach /Volumes/scipy-stack-py27-1.0
	python -c 'import numpy, scipy, matplotlib, IPython'

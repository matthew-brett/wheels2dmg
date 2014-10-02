# Requires GNU Make extensions

# Set W2D_PY_VERSION env var to change tested Python version
W2D_PY_VERSION ?= $(lastword $(shell python -ESV 2>&1))
# Set W2D_GET_PIP_URL to local get-pip.py path
W2D_GET_PIP_URL ?=

# Set get-pip-url option if env var not empty
ifneq ($(W2D_GET_PIP_URL),)
    GET_PIP=--get-pip-url=$(W2D_GET_PIP_URL)
endif
# Logic for getting Python major.minor version strings
PY_VERS = $(subst ., ,$(W2D_PY_VERSION))
PY_MAJ = $(word 1, $(PY_VERS))
PY_MIN = $(word 2, $(PY_VERS))
PY_MM = $(PY_MAJ)$(PY_MIN)
PY_MDM = $(PY_MAJ).$(PY_MIN)

all: clean
	mkdir dist
	python ./scripts/wheels2dmg scipy-stack 1.0 \
	    numpy scipy matplotlib ipython[notebook] $(GET_PIP) \
	    --dmg-out-dir=dist \
	    --dmg-build-dir=tmp \
	    --scratch-dir=scratch \
	    --python-version=$(W2D_PY_VERSION) \
	    --no-index

clean:
	rm -rf dist tmp scratch

install:
	- sudo pip$(PY_MDM) uninstall -y numpy scipy matplotlib ipython[notebook]
	hdiutil attach dist/scipy-stack-py$(PY_MM)-1.0.dmg
	sudo installer -pkg \
	    /Volumes/scipy-stack-py$(PY_MM)-1.0/scipy-stack-py$(PY_MM)-1.0.pkg \
	    -verbose -target /
	hdiutil detach /Volumes/scipy-stack-py$(PY_MM)-1.0
	python$(PY_MDM) -c 'import numpy, scipy, matplotlib, IPython'

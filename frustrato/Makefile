all: rpms

PYOPENSTACK = $(CURDIR)
FRUSTRATO = $(PYOPENSTACK)/frustrato
RPMBUILD = $(FRUSTRATO)/build

ORIG_SPEC = $(FRUSTRATO)/centos/SPECS/python-openstackclient.spec
SPEC = $(FRUSTRATO)/build/SPECS/python-openstackclient.spec

VERSION = $(shell grep "^Version:" $(ORIG_SPEC) | awk '{print $$2}')
PBR_VERSION = $(shell python $(PYOPENSTACK)/setup.py --version)
BUILDID = $(subst $(VERSION),,$(PBR_VERSION))

PYOPENSTACK_TAR = python-openstackclient.tar.gz
SOURCE0 = $(RPMBUILD)/SOURCES/$(PYOPENSTACK_TAR)

rpms: pyopenstack

submit:
	solvent submitproduct rpms $(RPMBUILD)/RPMS/noarch

approve:
	solvent approve --product=rpms

prepareForCleanBuild:
	sudo yum-builddep --assumeyes $(ORIG_SPEC)

clean:
	sudo rm -fr $(RPMBUILD)

sources: clean
	mkdir -p $(RPMBUILD)/SOURCES
	python $(PYOPENSTACK)/setup.py sdist
	mv $(PYOPENSTACK)/dist/python-openstackclient-$(PBR_VERSION).tar.gz $(SOURCE0)

spec: clean
	mkdir -p $(dir $(SPEC))
	sed -e "s/^Source0:.*/Source0: $(PYOPENSTACK_TAR)/" $(ORIG_SPEC) > $(SPEC)

pyopenstack: sources spec
	rpmbuild -D "_topdir $(RPMBUILD)" -D "dist .el7_0" -D "buildid $(BUILDID)" -bb $(SPEC)

.PHONY: rpms

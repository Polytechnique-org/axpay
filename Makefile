MANAGE_PY = python manage.py
ROOT_DIR = axpay
SERVICES = www

MANAGE_OPTIONS = --noinput --traceback
RUN_OPTIONS = --traceback

# In order to help newcomers, this variable holds a full doc of the current Makefile.
# Please keep it up to date with regard to new commands.
#
# Structure:
# - Group commands in sections
# - Align command descriptions

define helpmsg
Makefile command help

The following commands are available.

- Running:
    run_www:    	Start a development server for the site on http://127.0.0.1:8000/
    shell:      	Open a development Python shell using the current database

- Preparation & compilation:
    makemessages:  	Update all .po files
    compilemessages:	Rebuild .mo files
    static:		Collect static files
    prepare:    	Perform all required preparation steps (collectstatic, po->mo, etc.)

- Database:
    resetdb:    	Reinitialize the database schema

- Testing:
    test:		Run the test suite

- Misc:
    clean:      	Cleanup all temporary files (*.pyc, ...)
    doc:        	Generate the documentation
    help:       	Display this help message
endef

default: help


all: prepare


help:
	@echo -n ""  # Don't display extra lines.
	$(info $(helpmsg))


.PHONY: all default help


# Running
# =======

run_www: static_www compilemessages
	$(MANAGE_PY) runserver $(RUN_OPTIONS) 8000

shell:
	$(MANAGE_PY) shell

.PHONY: run_www


# Preparation & compilation
# =========================

STATICS = $(addprefix static_,$(SERVICES))

static: $(STATICS)

$(STATICS): static_% :
	SERVICE=$* $(MANAGE_PY) collectstatic $(MANAGE_OPTIONS) --verbosity=0

PO_FILES = $(shell find $(ROOT_DIR) -name '*.po')

makemessages:
	cd $(ROOT_DIR) && django-admin.py makemessages --all --no-wrap

MO_FILES = $(PO_FILES:.po=.mo)
compilemessages: $(MO_FILES)

%.mo: %.po
	msgfmt --check-format -o $@ $<

prepare: compilemessages static

.PHONY: compilemessages makemesssages prepare static $(STATICS)


# Development
# ===========

TESTS = $(addprefix test_,$(SERVICES))
test: $(TESTS)
	@:

$(TESTS): test_% : static_%
	SERVICE=$* $(MANAGE_PY) test $(MANAGE_OPTIONS)

resetdb:
	rm -f db.sqlite
	$(MANAGE_PY) syncdb $(MANAGE_OPTIONS)

.PHONY: resetdb test $(TESTS)


# Continuous integration
# ======================

JENKINS_TARGETS = $(addprefix jenkins_,$(SERVICES))

jenkins: $(JENKINS_TARGETS)
	@:

$(JENKINS_TARGETS): jenkins_% : static_%
	@echo "Running tests on $*..."
	SERVICE=$* DEV_JENKINS=1 $(MANAGE_PY) test $(MANAGE_OPTIONS)


.PHONY: jenkins $(JENKINS_TARGETS)


# Misc
# ====

clean:
	find . "(" -name "*.pyc" -or -name "*.pyo" -or -name "*.mo" ")" -delete
	find . -type d -empty -delete
	rm -rf bal/static/*
	rm -rf reports/

doc:
	$(MAKE) -C doc html


.PHONY: clean doc


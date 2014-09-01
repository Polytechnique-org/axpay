MANAGE_PY = python3 manage.py
ROOT_DIR = axpay
DOC_DIR = docs
SERVICES = core www

MANAGE_OPTIONS = --traceback
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
    demodb:		Reinitialize the database to a demo-ready setup

- Quality:
    test:		Run the test suite
    pylint:		Check the code for coding style errors

- Misc:
    clean:      	Cleanup all temporary files (*.pyc, ...)
    doc:        	Generate the documentation
    viewdoc:		Open a web browser on the (local) documentation
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
	AXPAY_SERVICE=www $(MANAGE_PY) runserver $(RUN_OPTIONS) 8000

shell:
	$(MANAGE_PY) shell

.PHONY: run_www shell


# Preparation & compilation
# =========================

STATICS = $(addprefix static_,$(SERVICES))

static: $(STATICS)

$(STATICS): static_% :
	AXPAY_SERVICE=$* $(MANAGE_PY) collectstatic --noinput $(MANAGE_OPTIONS) --verbosity=0

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
	AXPAY_SERVICE=$* $(MANAGE_PY) test $(MANAGE_OPTIONS)

pylint:
	pylint --rcfile=.pylintrc --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" \
		--reports=no --output-format=colorized $(ROOT_DIR) || true

resetdb:
	rm -f db.sqlite
	$(MANAGE_PY) syncdb --noinput $(MANAGE_OPTIONS)

demodb: resetdb
	$(MANAGE_PY) loaddemo $(MANAGE_OPTIONS)

.PHONY: demodb resetdb test $(TESTS)


# Continuous integration
# ======================

JENKINS_TARGETS = $(addprefix jenkins_,$(SERVICES))

jenkins: $(JENKINS_TARGETS)
	@:

$(JENKINS_TARGETS): jenkins_% : static_%
	@echo "Running tests on $*..."
	AXPAY_SERVICE=$* DEV_JENKINS=1 $(MANAGE_PY) test $(MANAGE_OPTIONS)


.PHONY: jenkins $(JENKINS_TARGETS)


# Misc
# ====

clean:
	find . "(" -name "*.pyc" -or -name "*.pyo" -or -name "*.mo" ")" -delete
	find . -type d -empty -delete
	rm -rf axpay/static/*
	rm -rf reports/

doc:
	$(MAKE) -C $(DOC_DIR) html

viewdoc: doc
	python -c "import webbrowser; webbrowser.open('$(DOC_DIR)/_build/html/index.html')"


.PHONY: clean doc


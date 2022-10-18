# simple makefile wrapper to run waf

WAF_BINARY=$(PYTHON) ./buildtools/bin/waf
WAF=PYTHONHASHSEED=1 WAF_MAKE=1 $(WAF_BINARY)

all:
	$(WAF) build

install:
	$(WAF) install

uninstall:
	$(WAF) uninstall

test:
	$(WAF) test $(TEST_OPTIONS)

testonly:
	$(WAF) testonly $(TEST_OPTIONS)

perftest:
	$(WAF) test --perf-test $(TEST_OPTIONS)

help:
	@echo NOTE: to run extended waf options use $(WAF_BINARY) or modify your PATH
	$(WAF) --help

subunit-test:
	$(WAF) test --filtered-subunit $(TEST_OPTIONS)

testenv:
	$(WAF) test --testenv $(TEST_OPTIONS)

lcov:
	@echo usage:
	@echo ""
	@echo ./configure --enable-coverage
	@echo make -j
	@echo make test TESTS=mytest
	@echo make lcov
	@echo ""
	rm -f lcov.info
	lcov --capture --directory . --output-file lcov.info && \
	genhtml lcov.info --output-directory public --prefix=$$(pwd) && \
	echo Please open public/index.html in browser to view the coverage report

gdbtestenv:
	$(WAF) test --testenv --gdbtest $(TEST_OPTIONS)

quicktest:
	$(WAF) test --quick $(TEST_OPTIONS)

randomized-test:
	$(WAF) test --random-order $(TEST_OPTIONS)

testlist:
	$(WAF) test --list $(TEST_OPTIONS)

test-nopython:
	$(WAF) test --no-subunit-filter --test-list=selftest/no-python-tests.txt $(TEST_OPTIONS)

dist:
	touch .tmplock
	WAFLOCK=.tmplock $(WAF) dist

distcheck:
	touch .tmplock
	WAFLOCK=.tmplock $(WAF) distcheck

clean:
	$(WAF) clean

distclean:
	$(WAF) distclean

reconfigure: configure
	$(WAF) reconfigure

show_waf_options:
	$(WAF) --help

# some compatibility make targets
everything: all

testsuite: all

check: test

torture: all

# this should do an install as well, once install is finished
installcheck: test

etags:
	$(WAF) etags

ctags:
	$(WAF) ctags

pydoctor:
	$(WAF) pydoctor

pep8:
	$(WAF) pep8

# Adding force on the dependencies will force the target to be always rebuild form the Make
# point of view forcing make to invoke waf

bin/smbd: FORCE
	$(WAF) --targets=smbd/smbd

bin/winbindd: FORCE
	$(WAF) --targets=winbindd/winbindd

bin/nmbd: FORCE
	$(WAF) --targets=nmbd/nmbd

bin/smbclient: FORCE
	$(WAF) --targets=client/smbclient

# this allows for things like "make bin/smbtorture"
# mainly for the binary that don't have a broken mode like smbd that must
# be build with smbd/smbd
bin/%: FORCE
	$(WAF) --targets=$(subst bin/,,$@)

# Catch all rule to be able to call make service_repl in order to find the name
# of the submodule you want to build, look at the wscript
%:
	$(WAF) --targets=$@

# This rule has to be the last one
FORCE:
# Having .NOTPARALLEL will force make to do target once at a time but still -j
# will be present in the MAKEFLAGS that are in turn interpreted by WAF
# so only 1 waf at a time will be called but it will still be able to do parralel builds if
# instructed to do so
.NOTPARALLEL: %
.PHONY: FORCE everything testsuite check torture

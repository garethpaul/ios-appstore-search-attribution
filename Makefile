.PHONY: __repository-make-authority build check lint test
.SECONDEXPANSION:

ifneq ($(strip $(MAKEFILES)),)
$(error MAKEFILES must be empty; repository verification requires this Makefile to be loaded alone)
endif
override MAKEFILES :=
ifneq ($(origin MAKEFILE_LIST),file)
$(error MAKEFILE_LIST must not be overridden)
endif
override MAKEFILE_ROOT := $(shell sed_path=/usr/bin/sed; [ -x "$$sed_path" ] || sed_path=/bin/sed; [ -x "$$sed_path" ] || exit 1; path=$$(/usr/bin/printf '%s' '$(subst ','"'"',$(value MAKEFILE_LIST))' | "$$sed_path" 's/^ //'); [ -f "$$path" ] || exit 1; directory=$${path%/*}; [ "$$directory" != "$$path" ] || directory=.; CDPATH= cd -- "$$directory" && /bin/pwd -P)
ifeq ($(strip $(MAKEFILE_ROOT)),)
$(error repository Makefile must be loaded alone)
endif

build check lint test:: $$(if $$(filter file,$$(origin MAKEFILE_LIST)),,$$(error MAKEFILE_LIST must not be overridden))
build check lint test:: $$(if $$(shell sed_path=/usr/bin/sed && [ -x "$$$$sed_path" ] || sed_path=/bin/sed && [ -x "$$$$sed_path" ] && path=$$$$(printf '%s' '$$(subst ','"'"',$$(MAKEFILE_LIST))' | "$$$$sed_path" 's/^ //') && [ -f "$$$$path" ] && printf '%s' ok),,$$(error repository Makefile must be loaded alone))
build check lint test:: __repository-make-authority

__repository-make-authority::
	@:

lint::
	cd "$(MAKEFILE_ROOT)" && python3 scripts/check-baseline.py
	cd "$(MAKEFILE_ROOT)" && python3 scripts/test-make-spaced-path.py

test::
	cd "$(MAKEFILE_ROOT)" && scripts/run-xcode-tests.sh

build::
	cd "$(MAKEFILE_ROOT)" && xcodebuild build -project ios-search-ads-sample.xcodeproj -scheme ios-search-ads-sample -sdk iphonesimulator -derivedDataPath "$${TMPDIR:-/tmp}/ios-attribution-build" CODE_SIGNING_ALLOWED=NO

check::
	cd "$(MAKEFILE_ROOT)" && python3 scripts/check-baseline.py
	cd "$(MAKEFILE_ROOT)" && python3 -m unittest discover -s tests -p 'test_*.py'
	cd "$(MAKEFILE_ROOT)" && scripts/run-xcode-tests.sh
	cd "$(MAKEFILE_ROOT)" && python3 scripts/test-make-spaced-path.py

.PHONY: build check lint test

override empty :=
override space := $(empty) $(empty)
override makefile_space := __IOS_ATTRIBUTION_MAKEFILE_SPACE__
override encoded_makefile_list := $(patsubst $(makefile_space)%,%,$(subst $(space),$(makefile_space),$(MAKEFILE_LIST)))
override MAKEFILE_ROOT := $(subst $(makefile_space),$(space),$(dir $(abspath $(lastword $(encoded_makefile_list)))))

lint:
	cd "$(MAKEFILE_ROOT)" && python3 scripts/check-baseline.py
	cd "$(MAKEFILE_ROOT)" && python3 scripts/test-make-spaced-path.py

test:
	cd "$(MAKEFILE_ROOT)" && scripts/run-xcode-tests.sh

build:
	cd "$(MAKEFILE_ROOT)" && xcodebuild build -project ios-search-ads-sample.xcodeproj -scheme ios-search-ads-sample -sdk iphonesimulator -derivedDataPath "$${TMPDIR:-/tmp}/ios-attribution-build" CODE_SIGNING_ALLOWED=NO

check:
	cd "$(MAKEFILE_ROOT)" && python3 scripts/check-baseline.py
	cd "$(MAKEFILE_ROOT)" && python3 -m unittest discover -s tests -p 'test_*.py'
	cd "$(MAKEFILE_ROOT)" && scripts/run-xcode-tests.sh
	cd "$(MAKEFILE_ROOT)" && python3 scripts/test-make-spaced-path.py

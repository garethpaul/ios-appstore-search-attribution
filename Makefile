.PHONY: build check lint test

MAKEFILE_ROOT := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

lint:
	cd "$(MAKEFILE_ROOT)" && python3 scripts/check-baseline.py

test:
	cd "$(MAKEFILE_ROOT)" && scripts/run-xcode-tests.sh

build:
	cd "$(MAKEFILE_ROOT)" && xcodebuild build -project ios-search-ads-sample.xcodeproj -scheme ios-search-ads-sample -sdk iphonesimulator -derivedDataPath "$${TMPDIR:-/tmp}/ios-attribution-build" CODE_SIGNING_ALLOWED=NO

check:
	cd "$(MAKEFILE_ROOT)" && python3 scripts/check-baseline.py
	cd "$(MAKEFILE_ROOT)" && python3 -m unittest discover -s tests -p 'test_*.py'
	cd "$(MAKEFILE_ROOT)" && scripts/run-xcode-tests.sh

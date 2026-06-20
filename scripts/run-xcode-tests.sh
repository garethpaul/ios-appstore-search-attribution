#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if ! command -v xcodebuild >/dev/null 2>&1 || ! command -v xcrun >/dev/null 2>&1; then
  echo "Xcode is required for native attribution tests" >&2
  exit 1
fi

DEVICE_ID="$({ xcrun simctl list devices available -j; } | python3 -c '
import json, sys
devices = json.load(sys.stdin).get("devices", {})
iphones = [device for runtime in devices.values() for device in runtime if device.get("isAvailable") and device.get("name", "").startswith("iPhone")]
booted = next((device for device in iphones if device.get("state") == "Booted"), None)
selected = booted or (iphones[0] if iphones else None)
if selected is None:
    raise SystemExit("No available iPhone simulator")
print(selected["udid"])
')"

DERIVED_DATA="$(mktemp -d "${TMPDIR:-/tmp}/ios-attribution-derived.XXXXXX")"
trap 'rm -rf "$DERIVED_DATA"' EXIT

cd "$ROOT"
xcodebuild test \
  -project ios-search-ads-sample.xcodeproj \
  -scheme ios-search-ads-sample \
  -destination "platform=iOS Simulator,id=$DEVICE_ID" \
  -derivedDataPath "$DERIVED_DATA" \
  CODE_SIGNING_ALLOWED=NO

#!/usr/bin/env python3

import json
import re
import sys


IOS_RUNTIME_PREFIX = "com.apple.CoreSimulator.SimRuntime.iOS-"
IOS_RUNTIME_PATTERN = re.compile(r"^com\.apple\.CoreSimulator\.SimRuntime\.iOS-(\d+(?:-\d+)*)$")


class InventoryError(ValueError):
    pass


def parse_runtime_version(identifier):
    if not isinstance(identifier, str):
        raise InventoryError("Malformed simctl inventory: runtime identifier must be a string")
    if not identifier.startswith(IOS_RUNTIME_PREFIX):
        return None

    match = IOS_RUNTIME_PATTERN.fullmatch(identifier)
    if match is None:
        raise InventoryError(f"Malformed iOS runtime identifier: {identifier}")
    return tuple(int(component) for component in match.group(1).split("-"))


def select_device(inventory):
    if not isinstance(inventory, dict) or not isinstance(inventory.get("devices"), dict):
        raise InventoryError("Malformed simctl inventory: devices must be an object")

    candidates = []
    for runtime_identifier, devices in inventory["devices"].items():
        runtime_version = parse_runtime_version(runtime_identifier)
        if runtime_version is None:
            continue
        if not isinstance(devices, list):
            raise InventoryError("Malformed simctl inventory: runtime devices must be an array")

        for device in devices:
            if not isinstance(device, dict):
                raise InventoryError("Malformed simctl inventory: device must be an object")

            name = device.get("name")
            is_available = device.get("isAvailable")
            if not isinstance(name, str) or not isinstance(is_available, bool):
                raise InventoryError("Malformed simctl inventory: device name and availability are required")
            if not is_available or not name.startswith("iPhone"):
                continue

            udid = device.get("udid")
            state = device.get("state")
            if not isinstance(udid, str) or not udid or not isinstance(state, str):
                raise InventoryError("Malformed simctl inventory: available iPhone requires state and UDID")
            candidates.append((state == "Booted", runtime_version, name, udid))

    if not candidates:
        raise InventoryError("No available iPhone simulator")

    booted = [candidate for candidate in candidates if candidate[0]]
    eligible = booted or candidates
    newest_runtime = max(candidate[1] for candidate in eligible)
    newest = [candidate for candidate in eligible if candidate[1] == newest_runtime]
    return min(newest, key=lambda candidate: (candidate[2], candidate[3]))[3]


def main():
    try:
        inventory = json.load(sys.stdin)
        selected_udid = select_device(inventory)
    except json.JSONDecodeError as error:
        print(f"Malformed simctl JSON: {error.msg}", file=sys.stderr)
        return 1
    except InventoryError as error:
        print(str(error), file=sys.stderr)
        return 1

    print(selected_udid)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

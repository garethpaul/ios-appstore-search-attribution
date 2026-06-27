#!/usr/bin/env python3
import os
from pathlib import Path
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
CHILD_MARKER = "IOS_ATTRIBUTION_MAKE_SPACE_CHILD"


def run_make(make, arguments, caller, environment):
    return subprocess.run([make, *arguments], cwd=caller, env=environment,
                          text=True, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, timeout=180)


def main():
    if os.environ.get(CHILD_MARKER) == "1":
        return

    tracked = subprocess.check_output(
        ["git", "-C", str(ROOT), "ls-files", "-z"]
    ).decode().rstrip("\0").split("\0")
    with tempfile.TemporaryDirectory(prefix="ios-attribution-make-space-") as temporary:
        root = Path(temporary)
        copied = root / "repository with spaces"
        caller = root / "external caller"
        shutil.copytree(
            ROOT,
            copied,
            ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", "*.pyo"),
        )
        caller.mkdir()
        subprocess.run(["git", "-C", copied, "init", "-q"], check=True)
        subprocess.run(
            ["git", "-C", copied, "add", "-f", "-N", "--", *tracked],
            check=True,
        )
        environment = os.environ.copy()
        environment[CHILD_MARKER] = "1"
        make = environment.get("IOS_ATTRIBUTION_MAKE", "make")
        repository_makefile = str(copied / "Makefile")
        subprocess.run(
            [make, "-f", repository_makefile, "lint"],
            cwd=caller,
            env=environment,
            check=True,
            timeout=180,
        )
        extra = root / "extra.mk"
        extra.write_text(".PHONY: extra\nextra:\n\t@:\n", encoding="utf-8")
        preload_environment = environment.copy()
        preload_environment["MAKEFILES"] = str(extra)
        cases = (
            (run_make(make, ["-f", repository_makefile, "lint"], caller, preload_environment), "MAKEFILES must be empty"),
            (run_make(make, ["-f", repository_makefile, "MAKEFILE_LIST=untrusted", "lint"], caller, environment), "MAKEFILE_LIST must not be overridden"),
            (run_make(make, ["-f", str(extra), "-f", repository_makefile, "lint"], caller, environment), "repository Makefile must be loaded alone"),
            (run_make(make, ["-f", repository_makefile, "-f", str(extra), "lint"], caller, environment), "repository Makefile must be loaded alone"),
        )
        for result, message in cases:
            if result.returncode == 0 or message not in result.stderr:
                raise RuntimeError(message)


if __name__ == "__main__":
    main()

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "simctl"
SELECTOR = REPO_ROOT / "scripts" / "select-simulator.py"
RUN_XCODE_TESTS = REPO_ROOT / "scripts" / "run-xcode-tests.sh"
CHECK_BASELINE = REPO_ROOT / "scripts" / "check-baseline.py"


class SimulatorSelectionTests(unittest.TestCase):
    def test_reversed_runtime_order_selects_newest_runtime(self) -> None:
        for fixture_name in ("reversed-runtimes-a.json", "reversed-runtimes-b.json"):
            with self.subTest(fixture=fixture_name):
                result = self.run_selector_fixture(fixture_name)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, "NEWER-IPHONE\n")

    def test_booted_available_iphone_wins_over_newer_shutdown_device(self) -> None:
        result = self.run_selector_fixture("booted-preference.json")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "BOOTED-OLDER-IPHONE\n")

    def test_unavailable_and_non_iphone_devices_are_ignored(self) -> None:
        result = self.run_selector_fixture("unavailable-devices.json")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "AVAILABLE-IPHONE\n")

    def test_equal_runtime_uses_name_then_udid_tie_breaking(self) -> None:
        result = self.run_selector_fixture("stable-ties.json")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "AAA-UDID\n")

    def test_malformed_json_fails_explicitly(self) -> None:
        result = self.run_selector_fixture("malformed.json")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Malformed simctl JSON", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_malformed_inventory_shape_fails_explicitly(self) -> None:
        result = self.run_selector(json.dumps({"devices": []}))

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Malformed simctl inventory", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_malformed_ios_runtime_identifier_fails_explicitly(self) -> None:
        inventory = {
            "devices": {
                "com.apple.CoreSimulator.SimRuntime.iOS-future": [],
            }
        }

        result = self.run_selector(json.dumps(inventory))

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Malformed iOS runtime identifier", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_no_available_iphone_fails_explicitly(self) -> None:
        result = self.run_selector_fixture("no-available-iphone.json")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("No available iPhone simulator", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def run_selector_fixture(self, fixture_name: str) -> subprocess.CompletedProcess[str]:
        return self.run_selector((FIXTURES / fixture_name).read_text(encoding="utf-8"))

    def run_selector(self, inventory: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-I", str(SELECTOR)],
            cwd=REPO_ROOT,
            input=inventory,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )


class RunXcodeTestsIntegrationTests(unittest.TestCase):
    def test_uses_isolated_python_and_cleans_derived_data(self) -> None:
        result, invocation, derived_data = self.run_xcode_script(
            fixture_name="reversed-runtimes-a.json",
            xcrun_status=0,
            xcodebuild_status=0,
            hostile_pythonpath=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("platform=iOS Simulator,id=NEWER-IPHONE", invocation)
        self.assertFalse(derived_data.exists())

    def test_preserves_xcrun_failure_status_without_running_xcodebuild(self) -> None:
        result, invocation, _ = self.run_xcode_script(
            fixture_name="reversed-runtimes-a.json",
            xcrun_status=23,
            xcodebuild_status=0,
        )

        self.assertEqual(result.returncode, 23, result.stderr)
        self.assertEqual(invocation, "")

    def test_cleans_derived_data_after_xcodebuild_failure(self) -> None:
        result, invocation, derived_data = self.run_xcode_script(
            fixture_name="reversed-runtimes-a.json",
            xcrun_status=0,
            xcodebuild_status=17,
        )

        self.assertEqual(result.returncode, 17, result.stderr)
        self.assertIn("platform=iOS Simulator,id=NEWER-IPHONE", invocation)
        self.assertFalse(derived_data.exists())

    def run_xcode_script(
        self,
        fixture_name: str,
        xcrun_status: int,
        xcodebuild_status: int,
        hostile_pythonpath: bool = False,
    ) -> tuple[subprocess.CompletedProcess[str], str, Path]:
        temp_path = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, temp_path, True)
        fake_bin = temp_path / "bin"
        fake_bin.mkdir()
        invocation_path = temp_path / "xcodebuild-invocation.txt"
        derived_data_path = temp_path / "derived-data-path.txt"
        fixture_path = FIXTURES / fixture_name

        self.write_executable(
            fake_bin / "xcrun",
            f"""#!/bin/bash
cat {self.shell_quote(str(fixture_path))}
exit {xcrun_status}
""",
        )
        self.write_executable(
            fake_bin / "xcodebuild",
            f"""#!/bin/bash
printf '%s\\n' "$*" > {self.shell_quote(str(invocation_path))}
while [ "$#" -gt 0 ]; do
  if [ "$1" = "-derivedDataPath" ]; then
    shift
    printf '%s\\n' "$1" > {self.shell_quote(str(derived_data_path))}
    mkdir -p "$1"
    break
  fi
  shift
done
exit {xcodebuild_status}
""",
        )

        environment = os.environ.copy()
        environment["PATH"] = os.pathsep.join(
            [str(fake_bin), str(Path(sys.executable).parent), "/usr/bin", "/bin"]
        )
        environment["TMPDIR"] = str(temp_path)
        if hostile_pythonpath:
            hostile_modules = temp_path / "hostile-modules"
            hostile_modules.mkdir()
            (hostile_modules / "json.py").write_text(
                "raise SystemExit('hostile inherited PYTHONPATH was loaded')\n",
                encoding="utf-8",
            )
            environment["PYTHONPATH"] = str(hostile_modules)

        result = subprocess.run(
            ["/bin/bash", str(RUN_XCODE_TESTS)],
            cwd=temp_path,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        invocation = (
            invocation_path.read_text(encoding="utf-8") if invocation_path.exists() else ""
        )
        derived_data = (
            Path(derived_data_path.read_text(encoding="utf-8").strip())
            if derived_data_path.exists()
            else temp_path / "not-created"
        )
        return result, invocation, derived_data

    def write_executable(self, path: Path, contents: str) -> None:
        path.write_text(textwrap.dedent(contents), encoding="utf-8")
        path.chmod(0o755)

    def shell_quote(self, value: str) -> str:
        return "'" + value.replace("'", "'\\''") + "'"


class SimulatorSelectionBaselineTests(unittest.TestCase):
    def test_baseline_requires_selector_helper(self) -> None:
        result = self.run_mutated_baseline(lambda root: (root / "scripts" / "select-simulator.py").unlink())

        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("Required file is unsafe: scripts/select-simulator.py", result.stderr)

    def test_baseline_requires_isolated_selector_handoff(self) -> None:
        def remove_isolation(root: Path) -> None:
            runner = root / "scripts" / "run-xcode-tests.sh"
            runner.write_text(
                runner.read_text(encoding="utf-8").replace(
                    'python3 -I "$ROOT/scripts/select-simulator.py"',
                    'python3 "$ROOT/scripts/select-simulator.py"',
                ),
                encoding="utf-8",
            )

        result = self.run_mutated_baseline(remove_isolation)

        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("Simulator selection must use the isolated helper", result.stderr)

    def run_mutated_baseline(self, mutate) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "repo"
            shutil.copytree(
                REPO_ROOT,
                project_root,
                ignore=shutil.ignore_patterns(".git", ".ruff_cache", "__pycache__"),
            )
            mutate(project_root)
            return subprocess.run(
                [sys.executable, str(project_root / "scripts" / "check-baseline.py")],
                cwd=project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )


if __name__ == "__main__":
    unittest.main()

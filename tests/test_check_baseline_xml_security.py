from __future__ import annotations

import contextlib
import importlib.util
import io
import shutil
import subprocess
import tempfile
import unittest
from collections.abc import Callable
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
CHECK_BASELINE_PATH = REPO_ROOT / "scripts/check-baseline.py"
STORYBOARD_PATH = Path("ios-search-ads-sample/Base.lproj/Main.storyboard")


def load_check_baseline_module():
    spec = importlib.util.spec_from_file_location("check_baseline", CHECK_BASELINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load scripts/check-baseline.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CheckBaselineXMLSecurityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.check_baseline = load_check_baseline_module()

    def test_checked_in_storyboard_remains_compatible(self) -> None:
        result, stdout, stderr = self.run_baseline_with_storyboard(None)

        self.assertEqual(result, 0, stderr)
        self.assertIn("Attribution baseline passed", stdout)

    def test_make_check_runs_xml_security_tests(self) -> None:
        makefile = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")

        self.assertIn("python3 -m unittest discover -s tests -p 'test_*.py'", makefile)

    def test_rejects_doctype_with_external_file_entity(self) -> None:
        with tempfile.TemporaryDirectory() as external_dir:
            external_path = Path(external_dir) / "external-entity-sentinel.txt"
            external_path.write_text("EXTERNAL_ENTITY_SENTINEL", encoding="utf-8")
            xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE document [
  <!ENTITY xxe SYSTEM "file://{external_path}">
]>
<document type="com.apple.InterfaceBuilder3.CocoaTouch.Storyboard.XIB">
  &xxe;
</document>
"""

            result, _, stderr = self.run_baseline_with_storyboard(xml)

        self.assertUnsafeXMLRejected(result, stderr)
        self.assertNotIn("EXTERNAL_ENTITY_SENTINEL", stderr)

    def test_rejects_external_network_entity_attempt(self) -> None:
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE document [
  <!ENTITY xxe SYSTEM "http://127.0.0.1:9/metadata">
]>
<document type="com.apple.InterfaceBuilder3.CocoaTouch.Storyboard.XIB">
  &xxe;
</document>
"""

        with mock.patch("socket.create_connection", side_effect=AssertionError("network attempted")):
            result, _, stderr = self.run_baseline_with_storyboard(xml)

        self.assertUnsafeXMLRejected(result, stderr)

    def test_rejects_internal_entity_expansion(self) -> None:
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE document [
  <!ENTITY local "expanded">
]>
<document type="com.apple.InterfaceBuilder3.CocoaTouch.Storyboard.XIB">
  &local;
</document>
"""

        result, _, stderr = self.run_baseline_with_storyboard(xml)

        self.assertUnsafeXMLRejected(result, stderr)

    def test_rejects_billion_laughs_style_entity_expansion(self) -> None:
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE document [
  <!ENTITY lol "lol">
  <!ENTITY lol1 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
  <!ENTITY lol2 "&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;">
  <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
  <!ENTITY lol4 "&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;">
]>
<document type="com.apple.InterfaceBuilder3.CocoaTouch.Storyboard.XIB">
  &lol4;
</document>
"""

        result, _, stderr = self.run_baseline_with_storyboard(xml)

        self.assertUnsafeXMLRejected(result, stderr)

    def test_rejects_parameter_entities(self) -> None:
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE document [
  <!ENTITY % file SYSTEM "file:///etc/passwd">
  <!ENTITY % wrapper "<!ENTITY leak SYSTEM 'file:///etc/passwd'>">
  %wrapper;
]>
<document type="com.apple.InterfaceBuilder3.CocoaTouch.Storyboard.XIB">
  &leak;
</document>
"""

        result, _, stderr = self.run_baseline_with_storyboard(xml)

        self.assertUnsafeXMLRejected(result, stderr)

    def test_rejects_huge_storyboard_xml(self) -> None:
        xml = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<document type="com.apple.InterfaceBuilder3.CocoaTouch.Storyboard.XIB">\n'
            f'  <view>{"x" * (2 * 1024 * 1024)}</view>\n'
            "</document>\n"
        )

        result, _, stderr = self.run_baseline_with_storyboard(xml)

        self.assertUnsafeXMLRejected(result, stderr)

    def test_rejects_too_deep_storyboard_xml(self) -> None:
        depth = 320
        xml = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<document type="com.apple.InterfaceBuilder3.CocoaTouch.Storyboard.XIB">'
            + ("<view>" * depth)
            + ("</view>" * depth)
            + "</document>\n"
        )

        result, _, stderr = self.run_baseline_with_storyboard(xml)

        self.assertUnsafeXMLRejected(result, stderr)

    def test_rejects_too_many_storyboard_elements(self) -> None:
        element_count = self.check_baseline.MAX_STORYBOARD_XML_ELEMENTS
        xml = "<document>" + ("<view/>" * element_count) + "</document>"

        result, _, stderr = self.run_baseline_with_storyboard(xml)

        self.assertUnsafeXMLRejected(result, stderr)

    def test_rejects_too_many_attributes_on_one_element(self) -> None:
        attribute_count = self.check_baseline.MAX_STORYBOARD_XML_ATTRIBUTES + 1
        attributes = " ".join(f'a{index}="value"' for index in range(attribute_count))
        xml = f"<document {attributes}/>"

        result, _, stderr = self.run_baseline_with_storyboard(xml)

        self.assertUnsafeXMLRejected(result, stderr)

    def test_reports_malformed_xml_as_safe_metadata_failure(self) -> None:
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<document type="com.apple.InterfaceBuilder3.CocoaTouch.Storyboard.XIB">
  <view>
</document>
"""

        result, _, stderr = self.run_baseline_with_storyboard(xml)

        self.assertUnsafeXMLRejected(result, stderr)

    def test_reports_unknown_xml_encoding_as_safe_metadata_failure(self) -> None:
        xml = b'<?xml version="1.0" encoding="X-BOGUS"?><document/>'

        result, _, stderr = self.run_baseline_with_storyboard(xml)

        self.assertUnsafeXMLRejected(result, stderr)
        self.assertNotIn("Traceback", stderr)

    def test_rejects_doctype_behind_namespaces_and_encoding(self) -> None:
        xml = """<?xml version="1.0" encoding="UTF-16"?>
<!DOCTYPE ib:document [
  <!ENTITY local "expanded">
]>
<ib:document xmlns:ib="urn:storyboard" type="com.apple.InterfaceBuilder3.CocoaTouch.Storyboard.XIB">
  &local;
</ib:document>
""".encode("utf-16")

        result, _, stderr = self.run_baseline_with_storyboard(xml)

        self.assertUnsafeXMLRejected(result, stderr)

    def test_accepts_namespaced_utf16_storyboard_without_doctype(self) -> None:
        xml = """<?xml version="1.0" encoding="UTF-16"?>
<ib:document xmlns:ib="urn:storyboard" type="com.apple.InterfaceBuilder3.CocoaTouch.Storyboard.XIB">
  <ib:scenes/>
</ib:document>
""".encode("utf-16")

        result, stdout, stderr = self.run_baseline_with_storyboard(xml)

        self.assertEqual(result, 0, stderr)
        self.assertIn("Attribution baseline passed", stdout)

    def test_rejects_unbound_namespace_prefix(self) -> None:
        result, _, stderr = self.run_baseline_with_storyboard("<ib:document/>")

        self.assertUnsafeXMLRejected(result, stderr)

    def test_rejects_duplicate_attributes_with_same_expanded_name(self) -> None:
        xml = '<document xmlns:a="urn:storyboard" xmlns:b="urn:storyboard" a:id="1" b:id="2"/>'

        result, _, stderr = self.run_baseline_with_storyboard(xml)

        self.assertUnsafeXMLRejected(result, stderr)

    def test_rejects_storyboard_parent_directory_symlink(self) -> None:
        def replace_parent_with_symlink(project_root: Path) -> None:
            storyboard_parent = (project_root / STORYBOARD_PATH).parent
            external_parent = project_root.parent / "external-storyboard"
            external_parent.mkdir()
            shutil.copy2(storyboard_parent / STORYBOARD_PATH.name, external_parent / STORYBOARD_PATH.name)
            shutil.rmtree(storyboard_parent)
            storyboard_parent.symlink_to(external_parent, target_is_directory=True)

        result, _, stderr = self.run_baseline_with_storyboard(
            None,
            mutate_project=replace_parent_with_symlink,
        )

        self.assertUnsafePathRejected(result, stderr)

    def test_rejects_storyboard_file_symlink(self) -> None:
        def replace_file_with_symlink(project_root: Path) -> None:
            storyboard_path = project_root / STORYBOARD_PATH
            external_path = project_root.parent / "external-storyboard.xml"
            shutil.copy2(storyboard_path, external_path)
            storyboard_path.unlink()
            storyboard_path.symlink_to(external_path)

        result, _, stderr = self.run_baseline_with_storyboard(
            None,
            mutate_project=replace_file_with_symlink,
        )

        self.assertUnsafePathRejected(result, stderr)

    def assertUnsafeXMLRejected(self, result: int, stderr: str) -> None:
        self.assertEqual(result, 1, stderr)
        self.assertIn("Project metadata must parse safely", stderr)

    def assertUnsafePathRejected(self, result: int, stderr: str) -> None:
        self.assertEqual(result, 1, stderr)
        self.assertIn("Required file is unsafe", stderr)

    def run_baseline_with_storyboard(
        self,
        storyboard: str | bytes | None,
        mutate_project: Callable[[Path], None] | None = None,
    ) -> tuple[int, str, str]:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "repo"
            shutil.copytree(
                REPO_ROOT,
                project_root,
                ignore=shutil.ignore_patterns(".git", ".ruff_cache", "__pycache__"),
            )
            if storyboard is not None:
                path = project_root / STORYBOARD_PATH
                if isinstance(storyboard, bytes):
                    path.write_bytes(storyboard)
                else:
                    path.write_text(storyboard, encoding="utf-8")
            if mutate_project is not None:
                mutate_project(project_root)

            xcodebuild_result = subprocess.CompletedProcess(
                args=["xcodebuild", "-project", "ios-search-ads-sample.xcodeproj", "-list"],
                returncode=0,
                stdout="Schemes:\n    ios-search-ads-sample\n    ios-search-ads-sampleTests\n",
            )
            stdout = io.StringIO()
            stderr = io.StringIO()
            with (
                mock.patch.object(self.check_baseline, "ROOT", project_root),
                mock.patch.object(self.check_baseline.subprocess, "run", return_value=xcodebuild_result),
                contextlib.redirect_stdout(stdout),
                contextlib.redirect_stderr(stderr),
            ):
                result = self.check_baseline.main()

            return result, stdout.getvalue(), stderr.getvalue()


if __name__ == "__main__":
    unittest.main()

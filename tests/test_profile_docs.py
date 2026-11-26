"""Regression checks for the public GitHub profile documentation."""
from pathlib import Path
import re
import unittest
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_FILES = (ROOT / "README.md", ROOT / "SECURITY.md")


class ProfileDocumentationTests(unittest.TestCase):
    def test_required_documents_exist_and_are_nonempty(self):
        for path in MARKDOWN_FILES:
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file())
                self.assertGreater(len(path.read_text(encoding="utf-8").strip()), 0)

    def test_profile_readme_has_one_primary_heading(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        headings = re.findall(r"^# (.+)$", readme, flags=re.MULTILINE)
        self.assertEqual(headings, ["Gavin Schilling"])

    def test_markdown_links_are_secure_and_local_targets_exist(self):
        failures = []
        pattern = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
        for document in MARKDOWN_FILES:
            source = document.read_text(encoding="utf-8")
            for destination in pattern.findall(source):
                destination = destination.strip().split(maxsplit=1)[0].strip("<>")
                parsed = urlsplit(destination)
                if parsed.scheme:
                    if parsed.scheme not in {"https", "mailto"}:
                        failures.append(f"{document.name}: unsupported URL scheme in {destination}")
                    continue
                if destination.startswith("#") or not parsed.path:
                    continue
                target = (document.parent / unquote(parsed.path)).resolve()
                if not target.is_file():
                    failures.append(f"{document.name}: missing local target {destination}")
        self.assertEqual(failures, [], "\n".join(failures))

    def test_documents_have_no_trailing_whitespace(self):
        for document in MARKDOWN_FILES:
            with self.subTest(path=document.name):
                for number, line in enumerate(
                    document.read_text(encoding="utf-8").splitlines(), start=1
                ):
                    self.assertEqual(
                        line.rstrip(),
                        line,
                        f"{document.name}:{number} has trailing whitespace",
                    )


if __name__ == "__main__":
    unittest.main(verbosity=2)

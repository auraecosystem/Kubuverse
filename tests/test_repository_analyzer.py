import tempfile
import unittest
from pathlib import Path

from services.analyzer import _read_repository_files, _validate_repository_url


class RepositoryAnalyzerTests(unittest.TestCase):
    def test_accepts_public_github_repository_url(self):
        self.assertEqual(
            _validate_repository_url("https://github.com/octocat/Hello-World"),
            "https://github.com/octocat/Hello-World",
        )

    def test_rejects_non_github_and_non_https_urls(self):
        for value in (
            "http://github.com/octocat/Hello-World",
            "https://example.com/octocat/Hello-World",
            "https://user:password@github.com/octocat/Hello-World",
            "https://github.com/octocat/Hello-World/tree/main",
            "https://github.com/octocat/Hello-World?token=example",
        ):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    _validate_repository_url(value)

    def test_skips_environment_and_secret_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "README.md").write_text("safe documentation", encoding="utf-8")
            (root / ".env.production").write_text("API_KEY=do-not-send", encoding="utf-8")
            (root / "secrets.toml").write_text("TOKEN=do-not-send", encoding="utf-8")
            result = _read_repository_files(root)

        self.assertIn("safe documentation", result)
        self.assertNotIn("do-not-send", result)
        self.assertNotIn("API_KEY", result)


if __name__ == "__main__":
    unittest.main()

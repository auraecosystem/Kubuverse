"""Safe, bounded analysis of public GitHub repositories."""
from __future__ import annotations

import os
import re
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlsplit

from openai import AsyncOpenAI

_MAX_FILES = 20
_MAX_FILE_BYTES = 64 * 1024
_MAX_PROMPT_CHARS = 80_000
_GITHUB_REPO_PATH = re.compile(r"^/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:\.git)?/?$")


def _validate_repository_url(value: str) -> str:
    parsed = urlsplit(value)
    if (
        parsed.scheme != "https"
        or parsed.hostname != "github.com"
        or parsed.port not in (None, 443)
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
        or not _GITHUB_REPO_PATH.fullmatch(parsed.path)
    ):
        raise ValueError("Only public GitHub repository URLs are supported.")
    return value


def _read_repository_files(root: Path) -> str:
    sections: list[str] = []
    total_chars = 0
    count = 0
    excluded_names = {
        "secrets.toml", "credentials.json", "google_auth_credentials.py",
        "id_rsa", "id_ed25519", ".npmrc", ".pypirc",
    }
    excluded_suffixes = {
        ".pem", ".key", ".p12", ".pfx", ".keystore", ".credentials",
        ".secret",
    }
    excluded_dirs = {".git", ".ssh", ".aws", "secrets"}

    for current, dirs, filenames in os.walk(root, followlinks=False):
        dirs[:] = sorted(
            name for name in dirs
            if name.lower() not in excluded_dirs
            and not (Path(current) / name).is_symlink()
        )
        for filename in sorted(filenames):
            path = Path(current) / filename
            lower_name = filename.lower()
            if path.is_symlink() or lower_name.startswith(".env"):
                continue
            if lower_name in excluded_names or path.suffix.lower() in excluded_suffixes:
                continue
            try:
                if path.stat().st_size > _MAX_FILE_BYTES:
                    continue
                content = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue

            relative = path.relative_to(root).as_posix()
            section = f"\n\n### {relative}\n\n{content}"
            remaining = _MAX_PROMPT_CHARS - total_chars
            if remaining <= 0:
                return "".join(sections)
            sections.append(section[:remaining])
            total_chars += min(len(section), remaining)
            count += 1
            if count >= _MAX_FILES or total_chars >= _MAX_PROMPT_CHARS:
                return "".join(sections)
    return "".join(sections)


async def analyze_repo(repository_url: str) -> str:
    """Clone a public GitHub repository and summarize a bounded source sample."""
    url = _validate_repository_url(str(repository_url))
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("The AI provider is not configured.")

    with tempfile.TemporaryDirectory(prefix="kubuverse-analysis-") as temp:
        checkout = Path(temp) / "repository"
        env = os.environ.copy()
        env["GIT_TERMINAL_PROMPT"] = "0"
        env["GIT_CONFIG_NOSYSTEM"] = "1"
        subprocess.run(
            [
                "git",
                "-c", "protocol.ext.allow=never",
                "-c", "http.followRedirects=false",
                "clone", "--depth", "1", "--no-tags", "--",
                url, str(checkout),
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=45,
            env=env,
        )
        source = _read_repository_files(checkout)
        if not source.strip():
            raise ValueError("No readable source files were found in the repository.")

        async with AsyncOpenAI(api_key=api_key) as client:
            response = await client.chat.completions.create(
                model=os.getenv("KUBUVERSE_OPENAI_MODEL", "gpt-4o-mini"),
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a senior software engineer. Analyze only the "
                            "provided repository excerpts. Distinguish verified facts "
                            "from assumptions, prioritize security and correctness, "
                            "and never claim to have inspected files not supplied."
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            "Summarize this repository, identify concrete risks, and "
                            "propose a prioritized repair plan. Do not reproduce "
                            "credentials or secrets.\n\n" + source
                        ),
                    },
                ],
                temperature=0.2,
                max_tokens=1200,
            )
        return (response.choices[0].message.content or "").strip()

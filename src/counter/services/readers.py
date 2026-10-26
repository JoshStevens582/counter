from pathlib import Path

SUPPORTED_SUFFIXES = {".md", ".txt"}


def read_page_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def title_from_text(text: str, fallback: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip() or fallback
    return fallback


def title_from_path(path: Path) -> str:
    return path.stem.replace("-", " ").replace("_", " ").title()

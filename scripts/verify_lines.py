#!/usr/bin/env python3
"""Verify that every handwritten source file is strictly under 80 lines (<= 79 lines)."""
import sys
from pathlib import Path

IGNORED = {'.venv', 'node_modules', '.runtime', 'dist', '__pycache__', '.git', '.pytest_cache'}
EXTENSIONS = {'.py', '.js', '.jsx', '.ts', '.tsx', '.css', '.html', '.sql'}


def check_sources(root: Path) -> list[str]:
    oversized = []
    for path in sorted(root.rglob('*')):
        if path.suffix not in EXTENSIONS or IGNORED.intersection(path.parts) or not path.is_file():
            continue
        try:
            line_count = len(path.read_text(encoding='utf-8', errors='replace').splitlines())
        except Exception as exc:
            oversized.append(f'{path.relative_to(root)}: read error ({exc})')
            continue
        if line_count >= 80:
            oversized.append(f'{path.relative_to(root)}: {line_count} lines (limit: 79)')
    return oversized


def main():
    root = Path(__file__).resolve().parents[1]
    oversized = check_sources(root)
    if oversized:
        print(f"FAILED: Found {len(oversized)} files with >= 80 lines:\n" + "\n".join(oversized))
        sys.exit(1)
    print("SUCCESS: All human-maintained source files are under 80 lines (<= 79 lines).")


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Refresh the legacy integration directory and ZIP from the canonical skill.

Only the skill entrypoint, license, and Markdown references are packaged.
Existing unrelated files are not deleted. No network or credentials are used.
"""

from pathlib import Path
import zipfile


def main():
    root = Path(__file__).resolve().parents[1]
    source = root / "skills" / "listingsapi-integration"
    legacy = root / "listingsapi-integration"
    files = [source / "SKILL.md", source / "LICENSE", *sorted((source / "references").glob("*.md"))]
    for path in files:
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"Expected a regular package file: {path.relative_to(root)}")
    for path in files:
        target = legacy / path.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.is_symlink():
            raise ValueError(f"Refusing to overwrite a symlink: {target.relative_to(root)}")
        target.write_bytes(path.read_bytes())
    with zipfile.ZipFile(root / "listingsapi-integration.zip", "w") as archive:
        for path in files:
            name = "listingsapi-integration/" + path.relative_to(source).as_posix()
            entry = zipfile.ZipInfo(name, date_time=(2026, 10, 8, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, path.read_bytes())
    print(f"Packaged {len(files)} files into the legacy directory and ZIP.")


if __name__ == "__main__":
    main()

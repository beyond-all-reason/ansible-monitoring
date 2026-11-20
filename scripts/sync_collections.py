#!/usr/bin/env python3
"""Sync Ansible collections in .ansible/ to match requirements.yml."""

import argparse
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path


def _find_project_root() -> Path:
    for directory in (Path.cwd(), *Path.cwd().parents):
        if (directory / "requirements.yml").is_file():
            return directory
    sys.exit("Error: requirements.yml not found in current directory or any parent.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sync Ansible collections in .ansible/ to match requirements.yml."
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Reinstall collections even if requirements.yml has not changed.",
    )
    args = parser.parse_args()

    root = _find_project_root()
    req_file = root / "requirements.yml"
    ansible_dir = root / ".ansible"
    collections_dir = ansible_dir / "ansible_collections"
    stamp_file = ansible_dir / ".requirements.sha256"

    digest = hashlib.sha256(req_file.read_bytes()).hexdigest()

    if (
        not args.force
        and collections_dir.is_dir()
        and stamp_file.is_file()
        and stamp_file.read_text(encoding="utf-8").strip() == digest
    ):
        print("Collections are already up to date with requirements.yml.")
        return

    stamp_file.unlink(missing_ok=True)
    shutil.rmtree(collections_dir, ignore_errors=True)
    ansible_galaxy = Path(sys.executable).parent / "ansible-galaxy"
    subprocess.run(
        [str(ansible_galaxy), "collection", "install", "-r", str(req_file)],
        cwd=root,
        check=True,
    )
    ansible_dir.mkdir(parents=True, exist_ok=True)
    stamp_file.write_text(digest + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

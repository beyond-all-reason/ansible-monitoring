from __future__ import annotations

DOCUMENTATION = """
    name: check_deps
    type: aggregate
    short_description: Verify uv run environment and synced Ansible collections
    description:
      - Verifies before running a playbook that Ansible was launched via `uv run`
        in this project's virtualenv and that .ansible/ collections were synced
        for the current requirements.yml.
      - Aborts playbook execution with a non-zero exit code on any mismatch.
"""

import hashlib
import os
import sys
from pathlib import Path

from ansible.plugins.callback import CallbackBase


class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = "aggregate"
    CALLBACK_NAME = "check_deps"
    CALLBACK_NEEDS_ENABLED = True

    def v2_playbook_on_start(self, playbook):
        root = Path(getattr(playbook, "_basedir", None) or Path.cwd()).resolve()
        errors: list[str] = []

        if (root / "pyproject.toml").is_file():
            expected_venv = Path(os.environ.get("UV_PROJECT_ENVIRONMENT") or (root / ".venv")).resolve()
            if not os.environ.get("UV_RUN_RECURSION_DEPTH") or Path(sys.prefix).resolve() != expected_venv:
                errors.append(
                    "  - Must be run via `uv run ansible-playbook ...` in this project's virtualenv."
                )

        req_path = root / "requirements.yml"
        if req_path.is_file():
            expected_hash = hashlib.sha256(req_path.read_bytes()).hexdigest()
            stamp_path = root / ".ansible" / ".requirements.sha256"
            actual_hash = stamp_path.read_text(encoding="utf-8").strip() if stamp_path.is_file() else None
            if actual_hash != expected_hash:
                errors.append(
                    "  - Installed collections do not match requirements.yml. "
                    "Run `uv run sync-collections`."
                )

        if errors:
            self._display.error("Environment check failed:\n" + "\n".join(errors))
            sys.exit(1)

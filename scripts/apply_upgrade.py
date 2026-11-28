#!/usr/bin/env python3
"""Move staged dot-files into place and patch two small existing files.

GitHub's web upload skips folders that start with a dot, so they were
uploaded under _dot/. Run once from the repo root:

    python3 scripts/apply_upgrade.py

Safe to run twice.
"""

import shutil
import sys
from pathlib import Path

ROOT = Path.cwd()
STAGE = ROOT / "_dot"
MOVES = {
    "github": ".github",
    "devcontainer": ".devcontainer",
    "pre-commit-config.yaml": ".pre-commit-config.yaml",
}

DECISIONS_BLOCK = """
## 2026-11-27 decisions
- **6-day finish.** Replit Core ends 3 Dec, so the remaining modules are
  compressed into 6 days (see PLAN.md). Cut list agreed: radiology, OCR, SMS,
  doctor-patient chat, chronic charts, reminders, model-based triage.
- **Leave Replit.** Development moves to GitHub Codespaces or local; Replit is
  optional. Reason: Replit's free plan has limited compute and no Full build.
  See docs/DEV_ENVIRONMENT.md.
- **Risk-based review.** The other engineer approves auth, consent, audit, AI
  safety, security code, migrations and CI changes. Everything else
  self-merges on green CI. CODEOWNERS requests reviews automatically.
- **Migrations tested on Postgres in CI** (new `migrations` job), because unit
  tests use SQLite.
- **Repo is public.** Synthetic data only, no secrets, ever.
"""

REPLIT_NOTE = """
## Replit is optional from 3 Dec
Replit Core ends on 3 Dec. Use GitHub Codespaces or a local machine instead
(see docs/DEV_ENVIRONMENT.md). Nothing in the repo depends on Replit.
"""


def move_stage() -> None:
    if not STAGE.exists():
        print("No _dot folder found; skipping dot-file step.")
        return
    for name, target in MOVES.items():
        src, dst = STAGE / name, ROOT / target
        if not src.exists():
            print(f"  missing in stage: {name}")
            continue
        if src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dst)
        print(f"  placed {target}")
    shutil.rmtree(STAGE)
    print("  removed _dot/")


def patch_vite() -> None:
    path = ROOT / "frontend" / "vite.config.ts"
    if not path.exists():
        print("  vite.config.ts not found; skipping")
        return
    text = path.read_text(encoding="utf-8")
    if ".app.github.dev" in text:
        print("  vite.config.ts already allows Codespaces")
        return
    old = 'allowedHosts: [".replit.dev"]'
    if old not in text:
        print(
            "  WARNING: edit frontend/vite.config.ts by hand: "
            'add ".app.github.dev" to allowedHosts'
        )
        return
    new = 'allowedHosts: [".replit.dev", ".app.github.dev"]'
    path.write_text(text.replace(old, new), encoding="utf-8")
    print("  vite.config.ts now allows Codespaces")


TIDY = [
    "frontend/src/i18n/ar.json",
    "backend/app/__init__.py",
    "backend/app/core/__init__.py",
    "backend/app/db/__init__.py",
]


def tidy_whitespace() -> None:
    """Strip trailing spaces and end files with one newline (pre-commit would)."""
    for name in TIDY:
        path = ROOT / name
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        fixed = "\n".join(line.rstrip() for line in text.split("\n")).rstrip("\n")
        fixed = fixed + "\n" if fixed else ""
        if fixed != text:
            path.write_text(fixed, encoding="utf-8")
            print(f"  tidied {name}")


def append_once(name: str, marker: str, block: str) -> None:
    path = ROOT / name
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    if marker in text:
        print(f"  {name} already updated")
        return
    path.write_text(text.rstrip("\n") + "\n" + block, encoding="utf-8")
    print(f"  {name} updated")


def main() -> None:
    if not (ROOT / "pyproject.toml").exists():
        sys.exit("Run this from the repo root (the folder with pyproject.toml).")
    print("Applying workflow upgrade...")
    move_stage()
    patch_vite()
    tidy_whitespace()
    append_once("DECISIONS.md", "2026-11-27 decisions", DECISIONS_BLOCK)
    append_once("replit.md", "Replit is optional from 3 Dec", REPLIT_NOTE)
    print("Done. Next: git add -A && git commit -m 'chore: workflow upgrade'")


if __name__ == "__main__":
    main()

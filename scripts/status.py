#!/usr/bin/env python3
"""Show progress against PLAN.md plus a short git summary.

python3 scripts/status.py             full report (paste it to Claude)
python3 scripts/status.py --summary   Markdown only (used by CI)
"""

import re
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLAN = ROOT / "PLAN.md"

HEADING = re.compile(r"^#{2,3} (?P<title>.+)$")
TASK = re.compile(r"^- \[(?P<done>[ xX])\] (?:\[(?P<owner>[^\]]+)\] )?(?P<text>.+)$")
DATED = re.compile(r"^\w{3} (?P<day>\d{1,2}) (?P<mon>\w{3})")
MONTHS = {
    m: i
    for i, m in enumerate(
        "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split(), start=1
    )
}


class Section:
    def __init__(self, title: str) -> None:
        self.title = title
        self.tasks: list[tuple[bool, str, str]] = []  # done, owner, text

    @property
    def done(self) -> int:
        return sum(1 for t in self.tasks if t[0])

    @property
    def when(self) -> date | None:
        match = DATED.match(self.title)
        if not match or match["mon"] not in MONTHS:
            return None
        return date(date.today().year, MONTHS[match["mon"]], int(match["day"]))


def parse_plan() -> list[Section]:
    sections: list[Section] = []
    current: Section | None = None
    for line in PLAN.read_text(encoding="utf-8").splitlines():
        heading = HEADING.match(line)
        if heading:
            current = Section(heading["title"].strip())
            sections.append(current)
            continue
        task = TASK.match(line)
        if task and current is not None:
            current.tasks.append(
                (task["done"].lower() == "x", task["owner"] or "-", task["text"])
            )
    return [s for s in sections if s.tasks]


def bar(done: int, total: int, width: int = 20) -> str:
    filled = round(width * done / total) if total else 0
    return "#" * filled + "-" * (width - filled)


def git(*args: str) -> str:
    try:
        result = subprocess.run(
            ["git", *args], capture_output=True, text=True, cwd=ROOT, check=False
        )
    except FileNotFoundError:
        return ""
    return result.stdout.strip()


def summary(sections: list[Section]) -> str:
    total = sum(len(s.tasks) for s in sections)
    done = sum(s.done for s in sections)
    pct = round(100 * done / total) if total else 0
    lines = [
        f"### Plan progress: {done}/{total} tasks ({pct}%)",
        "",
        "| Section | Done |",
        "|---|---|",
    ]
    for s in sections:
        lines.append(f"| {s.title} | {s.done}/{len(s.tasks)} |")
    return "\n".join(lines)


def report(sections: list[Section]) -> str:
    today = date.today()
    total = sum(len(s.tasks) for s in sections)
    done = sum(s.done for s in sections)
    pct = round(100 * done / total) if total else 0
    out = [
        f"PLAN STATUS  {today:%a %d %b %Y}",
        f"Overall: {done}/{total} tasks ({pct}%)  [{bar(done, total)}]",
        "",
    ]
    width = max(len(s.title) for s in sections) + 2
    for s in sections:
        marker = ""
        if s.when == today:
            marker = "  <- today"
        elif s.when and s.when < today and s.done < len(s.tasks):
            marker = "  <- BEHIND"
        out.append(f"{s.title:<{width}} {s.done}/{len(s.tasks)}{marker}")

    owners: dict[str, list[int]] = {}
    for s in sections:
        for is_done, owner, _ in s.tasks:
            counts = owners.setdefault(owner, [0, 0])
            counts[1] += 1
            counts[0] += int(is_done)
    people = ", ".join(f"{o} {d}/{t}" for o, (d, t) in owners.items())
    out += ["", f"By person: {people}"]

    pending = [s for s in sections if s.done < len(s.tasks)]
    if pending:
        out += ["", f"Next up ({pending[0].title}):"]
        for is_done, owner, text in pending[0].tasks:
            if not is_done:
                out.append(f"  - [{owner}] {text[:100]}")

    branch = git("branch", "--show-current") or "(unknown)"
    dirty = len([ln for ln in git("status", "--porcelain").splitlines() if ln])
    remotes = [
        b.strip()
        for b in git("branch", "-r").splitlines()
        if "->" not in b and b.strip() != "origin/main"
    ]
    out += ["", f"GIT: branch {branch}, {dirty} uncommitted file(s)"]
    out.append("Last commits on main:")
    log = git(
        "log", "origin/main", "-5", "--pretty=format:%h %ad %an: %s", "--date=short"
    )
    out += [f"  {ln}" for ln in log.splitlines()]
    out.append(f"Other remote branches: {len(remotes)} (delete merged ones)")
    return "\n".join(out)


def main() -> None:
    if not PLAN.exists():
        sys.exit("PLAN.md not found")
    sections = parse_plan()
    print(summary(sections) if "--summary" in sys.argv else report(sections))


if __name__ == "__main__":
    main()

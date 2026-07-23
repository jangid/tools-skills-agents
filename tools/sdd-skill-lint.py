#!/usr/bin/env python3
"""sdd-skill-lint — consistency linter for the SDD skill suite.

Catches the classes of cross-skill drift found in the 2026-07-23 audit:

  * malformed or mismatched SKILL.md frontmatter (name != directory, missing
    description, orphan skill directories, agent files without frontmatter)
  * descriptions that violate the repo quality check "state when to use AND
    when not to use"
  * forbidden stale phrases that earlier audits removed (e.g. "upgrade to v2",
    "assign new domain prefixes") — each rule may allowlist legitimate
    negative mentions or historical citations
  * required cross-file contract markers (e.g. the `**Depends on**` field must
    exist in sdd-plan, `{qimpl_block}` in fan-out.md) so a contract edited in
    one file cannot silently vanish from its counterpart
  * duplicate/broken ordinals in numbered lists outside code fences
  * relative Markdown links that do not resolve

Usage:
  tools/sdd-skill-lint.py [REPO_ROOT]   # lint (default: repo containing this script)
  tools/sdd-skill-lint.py --self-test   # run built-in fixture tests
  tools/sdd-skill-lint.py --help

Exit codes: 0 = clean, 1 = findings, 2 = usage/internal error.
"""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path

# ---------------------------------------------------------------------------
# Rule tables — extend these when a new audit closes a new class of drift.
# ---------------------------------------------------------------------------

# Phrases that must not (re)appear. `allow` regexes whitelist matching lines
# (negative mentions, historical citations). `files` limits the rule's scope
# to paths containing that substring; None means every linted file.
FORBIDDEN = [
    {
        "pattern": r"docs/spikes",
        "files": None,
        # sdd-implement's "do not create docs/spikes" negative mention and the
        # citations of the shipped RS-006 artifact are legitimate.
        "allow": [r"Do not create a separate", r"dispatch-concurrency"],
        "reason": "spike artifacts belong under docs/research/RS-* (audit F1)",
    },
    {"pattern": r"assign new domain prefixes", "files": None, "allow": [],
     "reason": "file splits must keep requirement IDs permanent (audit F3)"},
    {"pattern": r"upgrade to v2", "files": None, "allow": [],
     "reason": "version-check wording must not hardcode v2 (audit F13)"},
    {"pattern": r"start fresh with v2", "files": None, "allow": [],
     "reason": "greenfield wording must not hardcode v2 (final review #1)"},
    {"pattern": r"30 min max", "files": None, "allow": [],
     "reason": "budgets are stated in observable units (audit P3)"},
    {"pattern": r"budget: 30min", "files": None, "allow": [],
     "reason": "budgets are stated in observable units (audit P3)"},
    {"pattern": r"\[Priority:", "files": None, "allow": [r"no separate"],
     "reason": "priority is encoded by the modal verb only (audit P7)"},
    {"pattern": r"no plan index in v4", "files": None, "allow": [],
     "reason": "v4 per-workstream plan indexes exist (audit F17)"},
    {"pattern": r"skills/\*/SKILL\.md", "files": "sdd-review", "allow": [],
     "reason": "sdd-review must not hardcode this repo's layout (audit F11)"},
    {"pattern": r"v1 limitations", "files": None, "allow": [],
     "reason": "stale USAGE heading (audit F14)"},
    {"pattern": r"version: 2\.0", "files": "sdd-migrate", "allow": [],
     "reason": "index version: is a content counter, not a format signal (audit F20)"},
    {"pattern": r"Co-Authored-By", "files": None, "allow": [],
     "reason": "repo convention: no attribution lines in committed content"},
]

# Contract markers that must keep existing where a counterpart file relies on
# them. `min` is the minimum occurrence count in that file.
REQUIRED = [
    ("skills/sdd-orchestrate/SKILL.md", r"research_id", 3,
     "kickoff research_id contract (audit F10) spans table/KICKOFF/picker"),
    ("skills/sdd-plan/SKILL.md", r"\*\*Depends on\*\*", 3,
     "canonical chunk-dependency field consumed by fan-out (audit F7)"),
    ("skills/sdd-orchestrate/references/fan-out.md", r"\{qimpl_block\}", 2,
     "per-leaf Q-IMPL block slot (audit F5): template + slot contract"),
    ("skills/sdd-implement/SKILL.md", r"Parallel-dispatch exception", 1,
     "leaf-side half of the Q-IMPL block contract (audit F5)"),
    ("skills/sdd-plan/SKILL.md", r"last_updated: YYYY-MM-DD", 1,
     "single-milestone plan frontmatter that staleness checks key off (audit F2)"),
    ("skills/sdd-research/SKILL.md", r"early_exit: true", 1,
     "research early-exit marker the orchestrate picker relies on"),
    ("skills/sdd-review/SKILL.md", r"`questions:` frontmatter", 1,
     "research review reads questions from findings frontmatter (audit F9)"),
    ("skills/sdd-orchestrate/references/dispatch-templates.md", r"non-interactive", 2,
     "both pipeline and review dispatch templates carry the clause (audit F15)"),
    ("skills/sdd-implement/SKILL.md", r"status:.*`active`", 1,
     "plan status lifecycle executor: planned→active (final review #5)"),
    ("skills/sdd-implement/SKILL.md", r"status:.*`complete`", 1,
     "plan status lifecycle executor: →complete (final review #5)"),
]

# Every phase skill gates its layout on the version marker.
VERSION_GATED_SKILLS = [
    "sdd-research", "sdd-requirements", "sdd-specs", "sdd-plan",
    "sdd-implement", "sdd-verify", "sdd-replan", "sdd-migrate", "sdd-orchestrate",
]

# The seven skills that carry the collapsed v4 ownership summary (audit P1).
V4_CONTRACT_SKILLS = [
    "sdd-research", "sdd-requirements", "sdd-specs", "sdd-plan",
    "sdd-implement", "sdd-verify", "sdd-replan",
]

# Description must state when NOT to use the skill (repo quality check).
NOT_USE_RE = re.compile(r"\b(Skip|Do NOT|Do not use|not for)\b", re.IGNORECASE)


class Linter:
    def __init__(self, root: Path):
        self.root = root
        self.findings: list[str] = []

    # -- helpers ------------------------------------------------------------

    def flag(self, path: Path, line_no: int | None, rule: str, msg: str) -> None:
        rel = path.relative_to(self.root) if path.is_absolute() else path
        loc = f"{rel}:{line_no}" if line_no else str(rel)
        self.findings.append(f"{loc}: [{rule}] {msg}")

    def skill_files(self) -> list[Path]:
        """All lintable Markdown files under skills/ (SKILL.md, USAGE.md, references)."""
        return sorted((self.root / "skills").rglob("*.md")) if (self.root / "skills").is_dir() else []

    @staticmethod
    def frontmatter(text: str) -> dict[str, str] | None:
        """Parse the leading YAML frontmatter block; minimal, stdlib-only.

        Returns key -> raw value (folded `>` blocks concatenated), or None if
        the file does not start with a well-formed `---` block.
        """
        lines = text.splitlines()
        if not lines or lines[0].strip() != "---":
            return None
        fields: dict[str, str] = {}
        key = None
        for i, line in enumerate(lines[1:], start=1):
            if line.strip() == "---":
                return fields
            m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
            if m:
                key, val = m.group(1), m.group(2).strip()
                fields[key] = "" if val in (">", "|") else val
            elif key and (line.startswith("  ") or not line.strip()):
                fields[key] = (fields[key] + " " + line.strip()).strip()
            else:
                return None  # stray unindented line inside frontmatter
        return None  # unterminated block

    # -- checks -------------------------------------------------------------

    def check_structure(self) -> None:
        """Every skill dir has a SKILL.md; frontmatter well-formed; name matches dir."""
        skills_dir = self.root / "skills"
        if not skills_dir.is_dir():
            self.flag(self.root, None, "structure", "skills/ directory not found")
            return
        for d in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
            sk = d / "SKILL.md"
            if not sk.is_file():
                self.flag(d, None, "structure", "skill directory has no SKILL.md")
                continue
            fm = self.frontmatter(sk.read_text(encoding="utf-8"))
            if fm is None:
                self.flag(sk, 1, "frontmatter", "missing or malformed YAML frontmatter")
                continue
            name = fm.get("name", "")
            if not name:
                self.flag(sk, 1, "frontmatter", "frontmatter has no `name:`")
            elif name != d.name:
                self.flag(sk, 1, "frontmatter", f"name `{name}` != directory `{d.name}`")
            if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name or "x"):
                self.flag(sk, 1, "frontmatter", f"name `{name}` is not kebab-case")
            desc = fm.get("description", "")
            if not desc:
                self.flag(sk, 1, "frontmatter", "frontmatter has no `description:`")
            elif not NOT_USE_RE.search(desc):
                self.flag(sk, 1, "description",
                          "description never states when NOT to use the skill "
                          "(repo quality check)")
        # Agent files must carry frontmatter too (repo quality check).
        agents_dir = self.root / "agents"
        if agents_dir.is_dir():
            for a in sorted(agents_dir.glob("*.md")):
                fm = self.frontmatter(a.read_text(encoding="utf-8"))
                if fm is None:
                    self.flag(a, 1, "frontmatter", "agent file missing frontmatter")
                elif not fm.get("name"):
                    self.flag(a, 1, "frontmatter", "agent frontmatter has no `name:`")

    def check_forbidden(self) -> None:
        for f in self.skill_files():
            rel = str(f.relative_to(self.root))
            for rule in FORBIDDEN:
                if rule["files"] and rule["files"] not in rel:
                    continue
                pat = re.compile(rule["pattern"])
                allows = [re.compile(a) for a in rule["allow"]]
                for no, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
                    if pat.search(line) and not any(a.search(line) for a in allows):
                        self.flag(f, no, "forbidden",
                                  f"`{rule['pattern']}` — {rule['reason']}")

    def check_required(self) -> None:
        for rel, pattern, minimum, reason in REQUIRED:
            f = self.root / rel
            if not f.is_file():
                self.flag(Path(rel), None, "required", "file missing entirely")
                continue
            n = len(re.findall(pattern, f.read_text(encoding="utf-8")))
            if n < minimum:
                self.flag(f, None, "required",
                          f"`{pattern}` found {n}x, need >= {minimum} — {reason}")
        for name in VERSION_GATED_SKILLS:
            f = self.root / "skills" / name / "SKILL.md"
            if f.is_file() and "docs/.sdd-version" not in f.read_text(encoding="utf-8"):
                self.flag(f, None, "required", "never reads `docs/.sdd-version` "
                          "(every phase skill gates on the version marker)")
        for name in V4_CONTRACT_SKILLS:
            f = self.root / "skills" / name / "SKILL.md"
            if f.is_file() and "common v4 contract" not in f.read_text(encoding="utf-8"):
                self.flag(f, None, "required",
                          "lost the collapsed v4 ownership summary (audit P1)")

    def check_ordinals(self) -> None:
        """Numbered-list ordinals outside code fences must increment by one.

        Catches the `4.` / `4.` duplicate the final review found. Blocks reset
        on blank lines, headings, or unindented prose; indented lines are item
        continuations.
        """
        item_re = re.compile(r"^(\d+)\.\s")
        for f in self.skill_files():
            in_fence = False
            prev: int | None = None
            for no, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
                if line.lstrip().startswith("```"):
                    in_fence = not in_fence
                    prev = None
                    continue
                if in_fence:
                    continue
                m = item_re.match(line)
                if m:
                    n = int(m.group(1))
                    if prev is not None and n != prev + 1:
                        self.flag(f, no, "ordinal",
                                  f"list ordinal {n} follows {prev} (expected {prev + 1})")
                    prev = n
                elif line.startswith((" ", "\t")) and line.strip():
                    continue  # continuation of the current item
                else:
                    prev = None  # blank line / heading / prose ends the block

    def check_links(self) -> None:
        """Relative Markdown links must resolve on disk (skill-local files only)."""
        link_re = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
        for f in self.skill_files():
            in_fence = False
            for no, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
                if line.lstrip().startswith("```"):
                    in_fence = not in_fence
                    continue
                if in_fence:
                    continue  # links inside template examples are illustrative
                for target in link_re.findall(line):
                    if target.startswith(("http://", "https://", "mailto:", "#")):
                        continue
                    path = target.split("#", 1)[0]
                    if not path:
                        continue
                    if not (f.parent / path).exists():
                        self.flag(f, no, "link", f"broken relative link `{target}`")

    # -- driver -------------------------------------------------------------

    def run(self) -> int:
        self.check_structure()
        self.check_forbidden()
        self.check_required()
        self.check_ordinals()
        self.check_links()
        for finding in self.findings:
            print(finding)
        n_files = len(self.skill_files())
        if self.findings:
            print(f"\nFAIL: {len(self.findings)} finding(s) across {n_files} file(s)")
            return 1
        print(f"OK: {n_files} file(s) clean")
        return 0


# ---------------------------------------------------------------------------
# Self-test: seed a fixture repo with one violation per check and assert the
# linter reports each rule (and that a clean fixture passes).
# ---------------------------------------------------------------------------

def self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bad = root / "skills" / "bad-skill"
        bad.mkdir(parents=True)
        (bad / "SKILL.md").write_text(
            "---\n"
            "name: wrong-name\n"          # frontmatter: name != dir
            "description: >\n"
            "  Does things.\n"            # description: no skip clause
            "---\n\n"
            "# Bad\n\n"
            "Spike output goes to docs/spikes/topic.md.\n"   # forbidden
            "See [ref](references/missing.md).\n\n"          # broken link
            "1. one\n"
            "2. two\n"
            "2. dup\n",                   # ordinal
            encoding="utf-8",
        )
        (root / "skills" / "orphan-dir").mkdir()             # structure: no SKILL.md
        linter = Linter(root)
        # Scope the fixture run to checks that do not assume the real suite.
        linter.check_structure()
        linter.check_forbidden()
        linter.check_ordinals()
        linter.check_links()
        text = "\n".join(linter.findings)
        expected = ["[frontmatter]", "[description]", "[forbidden]",
                    "[ordinal]", "[link]", "[structure]"]
        missing = [e for e in expected if e not in text]
        if missing:
            print(f"SELF-TEST FAIL: rules never fired: {missing}\n\n{text}")
            return 1
        # A clean minimal skill must produce zero findings from these checks.
        good_root = root / "clean"
        good = good_root / "skills" / "good-skill"
        good.mkdir(parents=True)
        (good / "SKILL.md").write_text(
            "---\nname: good-skill\ndescription: >\n  Use for X. Skip for Y.\n---\n\n"
            "# Good\n\n1. one\n2. two\n",
            encoding="utf-8",
        )
        clean = Linter(good_root)
        clean.check_structure()
        clean.check_forbidden()
        clean.check_ordinals()
        clean.check_links()
        if clean.findings:
            print("SELF-TEST FAIL: clean fixture produced findings:\n"
                  + "\n".join(clean.findings))
            return 1
        print("SELF-TEST OK: all rule classes fire; clean fixture passes")
        return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="sdd-skill-lint",
        description="Consistency linter for the SDD skill suite "
                    "(frontmatter, drift phrases, contract markers, ordinals, links).",
    )
    ap.add_argument("root", nargs="?", default=None,
                    help="repository root to lint (default: repo containing this script)")
    ap.add_argument("--self-test", action="store_true",
                    help="run built-in fixture tests instead of linting")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parent.parent
    if not root.is_dir():
        print(f"error: {root} is not a directory", file=sys.stderr)
        return 2
    return Linter(root).run()


if __name__ == "__main__":
    sys.exit(main())

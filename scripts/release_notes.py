#!/usr/bin/env python3
"""Generate changelog drafts and release notes from git history."""

from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import re
import subprocess
import sys
from collections import OrderedDict
from pathlib import Path
from typing import Iterable


TYPE_TITLES = OrderedDict(
    [
        ("breaking", "Breaking Changes"),
        ("feat", "Features"),
        ("fix", "Fixes"),
        ("docs", "Documentation"),
        ("refactor", "Refactoring"),
        ("test", "Tests"),
        ("chore", "Chores"),
        ("style", "Style"),
        ("build", "Build"),
        ("ci", "CI"),
        ("other", "Other Changes"),
    ]
)

CONVENTIONAL_RE = re.compile(
    r"^(?P<type>[a-z]+)"
    r"(?:\((?P<scope>[^)]+)\))?"
    r"(?P<breaking>!)?:\s+"
    r"(?P<subject>.+?)"
    r"(?:\s+\(#(?P<pr>\d+)\))?$"
)
MERGE_PR_RE = re.compile(r"^Merge pull request #(?P<pr>\d+) from .+$")


@dataclasses.dataclass(frozen=True)
class CommitEntry:
    sha: str
    subject: str
    body: str
    type_name: str
    breaking: bool


def run_git(repo_root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo_root), *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return completed.stdout.strip()


def detect_repo_url(repo_root: Path) -> str:
    try:
        remote = run_git(repo_root, "remote", "get-url", "origin")
    except subprocess.CalledProcessError:
        return ""

    if remote.startswith("git@github.com:"):
        path = remote.removeprefix("git@github.com:")
        path = path.removesuffix(".git")
        return f"https://github.com/{path}"

    if remote.startswith("https://github.com/"):
        return remote.removesuffix(".git")

    return ""


def detect_previous_tag(repo_root: Path, to_ref: str) -> str:
    tags = run_git(
        repo_root,
        "tag",
        "--merged",
        to_ref,
        "--sort=-creatordate",
        "--list",
        "v*",
    )
    if not tags:
        return ""

    for tag in tags.splitlines():
        if tag != to_ref:
            return tag

    return ""


def git_range_commits(repo_root: Path, from_ref: str, to_ref: str) -> list[CommitEntry]:
    if from_ref:
        range_expr = f"{from_ref}..{to_ref}"
    else:
        range_expr = to_ref

    raw = subprocess.run(
        [
            "git",
            "-C",
            str(repo_root),
            "log",
            "--reverse",
            "--no-merges",
            f"--format=%H%x1f%s%x1f%b%x1e",
            range_expr,
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ).stdout

    entries: list[CommitEntry] = []
    for record in raw.split("\x1e"):
        record = record.strip()
        if not record:
            continue

        parts = record.split("\x1f")
        if len(parts) != 3:
            continue

        sha, subject, body = parts
        subject = subject.strip()
        body = body.strip()

        merge_pr_match = MERGE_PR_RE.match(subject)
        effective_subject = subject
        if merge_pr_match:
            body_head = next((line.strip() for line in body.splitlines() if line.strip()), "")
            if body_head:
                effective_subject = body_head
                pr_number = merge_pr_match.group("pr")
                if "(#" not in effective_subject:
                    effective_subject = f"{effective_subject} (#{pr_number})"

        match = CONVENTIONAL_RE.match(effective_subject)
        if match:
            type_name = match.group("type")
            breaking = bool(match.group("breaking")) or "BREAKING CHANGE:" in body
        else:
            type_name = "other"
            breaking = "BREAKING CHANGE:" in body

        if breaking:
            type_name = "breaking"

        entries.append(
            CommitEntry(
                sha=sha,
                subject=effective_subject,
                body=body,
                type_name=type_name,
                breaking=breaking,
            )
        )

    return entries


def summarize_entries(entries: Iterable[CommitEntry], repo_url: str) -> str:
    grouped: OrderedDict[str, list[CommitEntry]] = OrderedDict(
        (key, []) for key in TYPE_TITLES
    )
    for entry in entries:
        grouped.setdefault(entry.type_name, []).append(entry)

    lines: list[str] = []
    for type_name, title in TYPE_TITLES.items():
        bucket = grouped.get(type_name, [])
        if not bucket:
            continue

        lines.append(f"## {title}")
        lines.append("")
        for entry in bucket:
            short_sha = entry.sha[:7]
            if repo_url:
                sha_ref = f"[{short_sha}]({repo_url}/commit/{entry.sha})"
            else:
                sha_ref = f"`{short_sha}`"
            lines.append(f"- {entry.subject} ({sha_ref})")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def build_markdown(
    repo_root: Path,
    title: str,
    from_ref: str,
    to_ref: str,
    entries: list[CommitEntry],
) -> str:
    repo_url = detect_repo_url(repo_root)
    generated_at = dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="seconds")
    total = len(entries)
    from_label = from_ref or "initial history"

    lines: list[str] = [
        f"# {title}",
        "",
        f"- Range: `{from_label}..{to_ref}`",
        f"- Generated at: `{generated_at}`",
        f"- Total commits: `{total}`",
        "",
    ]

    if total == 0:
        lines.extend(
            [
                "## Summary",
                "",
                "No user-facing commits were found in this range.",
                "",
            ]
        )
        return "\n".join(lines).rstrip() + "\n"

    lines.extend(
        [
            "## Summary",
            "",
            f"Changes are grouped by Conventional Commit type for the `{from_label}` to `{to_ref}` range.",
            "",
        ]
    )
    lines.append(summarize_entries(entries, repo_url).rstrip())
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate changelog drafts or release notes from git history."
    )
    parser.add_argument("--repo-root", default=".", help="Repository root (default: .)")
    parser.add_argument("--from", dest="from_ref", default="", help="Lower bound ref")
    parser.add_argument("--to", dest="to_ref", default="HEAD", help="Upper bound ref")
    parser.add_argument("--title", default="", help="Document title")
    parser.add_argument(
        "--draft",
        action="store_true",
        help="Use the latest tag before --to as the lower bound and title the output as Unreleased",
    )
    parser.add_argument(
        "--output",
        default="",
        help="Write the generated Markdown to a file instead of stdout",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()

    from_ref = args.from_ref.strip()
    to_ref = args.to_ref.strip() or "HEAD"
    title = args.title.strip()

    if args.draft:
        if not from_ref:
            from_ref = detect_previous_tag(repo_root, to_ref)
        if not title:
            title = "Unreleased"
    else:
        if not title:
            title = to_ref
        if not from_ref:
            from_ref = detect_previous_tag(repo_root, to_ref)

    entries = git_range_commits(repo_root, from_ref, to_ref)
    markdown = build_markdown(repo_root, title, from_ref, to_ref, entries)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")
    else:
        sys.stdout.write(markdown)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

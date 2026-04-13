#!/usr/bin/env python3
"""Generate a weekly AI-assisted review digest for the navigation workspace."""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


GITHUB_API_BASE = "https://api.github.com"
DEFAULT_TIMEZONE = "Asia/Shanghai"
DEFAULT_AI_MODEL = "gpt-4.1-mini"


@dataclass(slots=True)
class RepoSpec:
    name: str
    owner: str
    repo: str
    version: str
    url: str
    local_path: str
    is_main: bool = False

    @property
    def full_name(self) -> str:
        return f"{self.owner}/{self.repo}"


@dataclass(slots=True)
class PRSnapshot:
    repo: str
    number: int
    title: str
    url: str
    author: str
    state: str
    draft: bool
    created_at: str
    updated_at: str
    merged_at: str | None
    labels: list[str]
    additions: int
    deletions: int
    changed_files: int
    files: list[str] = field(default_factory=list)
    ci_state: str = "unknown"
    ci_statuses: int = 0
    risk: str = "P2"
    risk_score: int = 40
    risk_reasons: list[str] = field(default_factory=list)


@dataclass(slots=True)
class MergedPRSnapshot:
    repo: str
    number: int
    title: str
    url: str
    author: str
    merged_at: str
    labels: list[str]


@dataclass(slots=True)
class RepoSnapshot:
    name: str
    full_name: str
    url: str
    manifest_version: str
    is_main: bool
    default_branch: str
    default_branch_sha: str | None
    default_branch_status: str
    latest_tag: str | None
    latest_release: str | None
    open_prs: list[PRSnapshot] = field(default_factory=list)
    merged_prs: list[MergedPRSnapshot] = field(default_factory=list)
    lock_changes: list[str] = field(default_factory=list)
    local_head: str | None = None
    local_branch: str | None = None
    local_dirty: bool = False


@dataclass(slots=True)
class WeeklyReviewData:
    generated_at: str
    period_start: str
    period_end: str
    timezone: str
    title: str
    ai_backend: str
    repo_count: int
    open_pr_count: int
    merged_pr_count: int
    p0_count: int
    p1_count: int
    p2_count: int
    p3_count: int
    repositories: list[RepoSnapshot]
    priority_queue: list[PRSnapshot]
    questions: list[str]
    ai_summary: str


class GitHubClient:
    def __init__(self, token: str, api_base: str = GITHUB_API_BASE) -> None:
        self._token = token.strip()
        self._api_base = api_base.rstrip("/")

    def request_json(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        payload: Any | None = None,
    ) -> Any:
        url = f"{self._api_base}{path}"
        if params:
            query = urllib.parse.urlencode(
                {key: value for key, value in params.items() if value is not None}
            )
            if query:
                url = f"{url}?{query}"

        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "navigation_3d-weekly-review",
        }
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"

        data = None
        if payload is not None:
            headers["Content-Type"] = "application/json"
            data = json.dumps(payload).encode("utf-8")

        request = urllib.request.Request(url, data=data, headers=headers, method=method)
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                with urllib.request.urlopen(request, timeout=60) as response:
                    body = response.read().decode("utf-8")
                break
            except urllib.error.HTTPError as exc:
                message = exc.read().decode("utf-8", errors="replace")
                raise RuntimeError(
                    f"GitHub API error for {path}: {exc.code} {message}"
                ) from exc
            except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as exc:
                last_error = exc
                if attempt < 2:
                    time.sleep(1.5 * (attempt + 1))
                    continue
                raise RuntimeError(f"GitHub API request failed for {path}: {exc}") from exc

        if not body:
            return None
        return json.loads(body)

    def paginate(
        self,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> list[Any]:
        page = 1
        items: list[Any] = []
        while True:
            query = dict(params or {})
            query["per_page"] = 100
            query["page"] = page
            chunk = self.request_json("GET", path, query)
            if not chunk:
                break
            if not isinstance(chunk, list):
                return [chunk]
            items.extend(chunk)
            if len(chunk) < 100:
                break
            page += 1
        return items

    def repo(self, full_name: str) -> dict[str, Any]:
        return self.request_json("GET", f"/repos/{full_name}")

    def branch(self, full_name: str, branch: str) -> dict[str, Any] | None:
        try:
            return self.request_json("GET", f"/repos/{full_name}/branches/{branch}")
        except RuntimeError:
            return None

    def open_pulls(self, full_name: str) -> list[dict[str, Any]]:
        return self.paginate(
            f"/repos/{full_name}/pulls",
            {"state": "open", "sort": "updated", "direction": "desc"},
        )

    def merged_pulls_since(
        self, full_name: str, since: dt.datetime
    ) -> list[dict[str, Any]]:
        merged: list[dict[str, Any]] = []
        cutoff = since.astimezone(dt.timezone.utc)
        page = 1
        while True:
            chunk = self.request_json(
                "GET",
                f"/repos/{full_name}/pulls",
                {
                    "state": "closed",
                    "sort": "updated",
                    "direction": "desc",
                    "per_page": 100,
                    "page": page,
                },
            )
            if not chunk:
                break
            if not isinstance(chunk, list):
                chunk = [chunk]
            stop = False
            for item in chunk:
                merged_at = parse_github_datetime(item.get("merged_at"))
                if merged_at is None:
                    continue
                if merged_at >= cutoff:
                    merged.append(item)
                else:
                    stop = True
            if stop or len(chunk) < 100:
                break
            page += 1
        return merged

    def pull(self, full_name: str, number: int) -> dict[str, Any]:
        return self.request_json("GET", f"/repos/{full_name}/pulls/{number}")

    def pull_files(self, full_name: str, number: int) -> list[dict[str, Any]]:
        return self.paginate(f"/repos/{full_name}/pulls/{number}/files")

    def combined_status(self, full_name: str, ref: str) -> dict[str, Any]:
        return self.request_json("GET", f"/repos/{full_name}/commits/{ref}/status")

    def latest_release(self, full_name: str) -> str | None:
        try:
            release = self.request_json("GET", f"/repos/{full_name}/releases/latest")
        except RuntimeError:
            return None
        if not release:
            return None
        return str(release.get("tag_name") or release.get("name") or "")

    def latest_tag(self, full_name: str) -> str | None:
        try:
            tags = self.paginate(f"/repos/{full_name}/tags")
        except RuntimeError:
            return None
        if not tags:
            return None
        return str(tags[0].get("name") or "")


def parse_github_slug(url: str) -> tuple[str, str]:
    patterns = [
        r"git@github\.com:(?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?$",
        r"https://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?$",
        r"ssh://git@github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?$",
    ]
    for pattern in patterns:
        match = re.match(pattern, url)
        if match:
            return match.group("owner"), match.group("repo")
    raise ValueError(f"Unsupported GitHub url: {url}")


def parse_private_repos(manifest_path: Path) -> list[RepoSpec]:
    specs: list[RepoSpec] = []
    current: dict[str, str] | None = None
    for raw_line in manifest_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        if stripped == "repositories:":
            continue
        if indent == 2 and stripped.endswith(":"):
            if current:
                specs.append(build_repo_spec(manifest_path, current))
            current = {"name": stripped[:-1]}
            continue
        if current and ":" in stripped:
            key, value = stripped.split(":", 1)
            current[key.strip()] = value.strip().strip("'\"")
    if current:
        specs.append(build_repo_spec(manifest_path, current))
    return specs


def build_repo_spec(manifest_path: Path, data: dict[str, str]) -> RepoSpec:
    name = data.get("name") or ""
    url = data.get("url") or ""
    version = data.get("version") or "develop"
    owner, repo = parse_github_slug(url)
    repo_root = manifest_path.resolve().parent.parent
    local_path = repo_root / "src" / name
    return RepoSpec(
        name=name,
        owner=owner,
        repo=repo,
        version=version,
        url=url,
        local_path=str(local_path),
    )


def detect_main_repo(repo_root: Path) -> RepoSpec:
    remote = git_output(repo_root, "remote", "get-url", "origin")
    owner, repo = parse_github_slug(remote)
    return RepoSpec(
        name=repo,
        owner=owner,
        repo=repo,
        version=git_output(repo_root, "branch", "--show-current") or "develop",
        url=remote,
        local_path=str(repo_root),
        is_main=True,
    )


def git_output(repo_root: Path, *args: str, allow_fail: bool = False) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo_root), *args],
        check=False if allow_fail else True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if completed.returncode != 0:
        if allow_fail:
            return ""
        raise RuntimeError(
            f"git {' '.join(args)} failed: {completed.stderr.strip() or completed.returncode}"
        )
    return completed.stdout.strip()


def current_git_token() -> str:
    for env_name in (
        "WEEKLY_REVIEW_GITHUB_TOKEN",
        "GH_TOKEN",
        "GITHUB_TOKEN",
    ):
        value = os.environ.get(env_name, "").strip()
        if value:
            return value
    completed = subprocess.run(
        ["gh", "auth", "status", "-h", "github.com", "-t"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if completed.returncode != 0:
        return ""
    output = "\n".join(part for part in (completed.stdout, completed.stderr) if part)
    for line in output.splitlines():
        match = re.search(r"Token:\s*(\S+)", line)
        if match:
            return match.group(1).strip()
    return ""


def parse_github_datetime(value: Any) -> dt.datetime | None:
    if not value:
        return None
    if isinstance(value, str):
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    return None


def ensure_timezone(name: str) -> ZoneInfo:
    try:
        return ZoneInfo(name)
    except Exception:
        return ZoneInfo(DEFAULT_TIMEZONE)


def local_git_snapshot(repo_root: Path, since: dt.datetime) -> tuple[str | None, str | None, bool, list[str]]:
    branch = git_output(repo_root, "branch", "--show-current", allow_fail=True) or None
    head = git_output(repo_root, "rev-parse", "HEAD", allow_fail=True) or None
    status = git_output(repo_root, "status", "--short", allow_fail=True)
    dirty = bool(status.strip())
    log_output = git_output(
        repo_root,
        "log",
        f"--since={since.astimezone(dt.timezone.utc).isoformat()}",
        "--pretty=format:%h %s",
        "--",
        "repos/private.repos",
        "CHANGELOG.md",
        "docs/releases",
        "docs/release-notes.md",
        allow_fail=True,
    )
    changes = [line.strip() for line in log_output.splitlines() if line.strip()]
    return branch, head, dirty, changes


def classify_risk(pr: PRSnapshot) -> tuple[str, int, list[str]]:
    reasons: list[str] = []
    score = 35
    title = pr.title.lower()
    labels = {label.lower() for label in pr.labels}

    if pr.draft:
        score = max(score, 65)
        reasons.append("draft PR，尚未准备好合并")
    if pr.ci_state == "failure":
        score = 100
        reasons.append("CI 失败")
    elif pr.ci_state == "pending":
        score = max(score, 75)
        reasons.append("CI 仍在运行或未完成")

    if pr.changed_files >= 20 or (pr.additions + pr.deletions) >= 600:
        score = max(score, 70)
        reasons.append("改动范围较大")

    if "breaking" in labels or "breaking" in title:
        score = 100
        reasons.append("存在破坏性变更提示")

    if "docs" in labels or "documentation" in labels or title.startswith("docs:"):
        score = min(score, 25)
        reasons.append("文档类改动")
    elif "chore" in labels or title.startswith("chore:"):
        score = min(score, 30)
        reasons.append("治理 / 脚本 / CI 类改动")
    elif "fix" in labels or title.startswith("fix:"):
        score = max(score, 45)
        reasons.append("修复类改动，需确认回归影响")
    else:
        score = max(score, 40)

    if score >= 90:
        level = "P0"
    elif score >= 70:
        level = "P1"
    elif score >= 40:
        level = "P2"
    else:
        level = "P3"

    if not reasons:
        reasons.append("常规变更")

    return level, score, reasons


def summarize_pr(
    client: GitHubClient,
    repo: RepoSpec,
    pr_item: dict[str, Any],
) -> PRSnapshot:
    number = int(pr_item["number"])
    detail = client.pull(repo.full_name, number)
    files = client.pull_files(repo.full_name, number)
    head_sha = str(detail.get("head", {}).get("sha") or "")
    status = client.combined_status(repo.full_name, head_sha) if head_sha else {}
    ci_state = str(status.get("state") or "unknown")
    labels = [
        str(label.get("name") or "")
        for label in detail.get("labels", [])
        if str(label.get("name") or "")
    ]
    snapshot = PRSnapshot(
        repo=repo.name,
        number=number,
        title=str(detail.get("title") or ""),
        url=str(detail.get("html_url") or pr_item.get("html_url") or ""),
        author=str(detail.get("user", {}).get("login") or ""),
        state=str(detail.get("state") or "open"),
        draft=bool(detail.get("draft", False)),
        created_at=str(detail.get("created_at") or ""),
        updated_at=str(detail.get("updated_at") or ""),
        merged_at=detail.get("merged_at"),
        labels=labels,
        additions=int(detail.get("additions") or 0),
        deletions=int(detail.get("deletions") or 0),
        changed_files=int(detail.get("changed_files") or len(files)),
        files=[str(item.get("filename") or "") for item in files if item.get("filename")],
        ci_state=ci_state,
        ci_statuses=len(status.get("statuses") or []),
    )
    snapshot.risk, snapshot.risk_score, snapshot.risk_reasons = classify_risk(snapshot)
    return snapshot


def summarize_merged_pr(pr_item: dict[str, Any], repo: RepoSpec) -> MergedPRSnapshot:
    return MergedPRSnapshot(
        repo=repo.name,
        number=int(pr_item["number"]),
        title=str(pr_item.get("title") or ""),
        url=str(pr_item.get("html_url") or ""),
        author=str(pr_item.get("user", {}).get("login") or ""),
        merged_at=str(pr_item.get("merged_at") or ""),
        labels=[
            str(label.get("name") or "")
            for label in pr_item.get("labels", [])
            if str(label.get("name") or "")
        ],
    )


def repository_health(
    client: GitHubClient,
    repo: RepoSpec,
    since: dt.datetime,
    repo_root: Path,
) -> RepoSnapshot:
    repo_info = client.repo(repo.full_name)
    default_branch = str(repo_info.get("default_branch") or repo.version or "develop")
    branch_info = client.branch(repo.full_name, default_branch)
    default_branch_sha = None
    default_branch_status = "unknown"
    if branch_info:
        default_branch_sha = str(branch_info.get("commit", {}).get("sha") or "")
        if default_branch_sha:
            default_branch_status = str(
                client.combined_status(repo.full_name, default_branch_sha).get("state")
                or "unknown"
            )

    open_items = client.open_pulls(repo.full_name)
    open_prs = [summarize_pr(client, repo, item) for item in open_items]
    merged_items = client.merged_pulls_since(repo.full_name, since)
    merged_prs = [summarize_merged_pr(item, repo) for item in merged_items]

    latest_release = client.latest_release(repo.full_name)
    latest_tag = client.latest_tag(repo.full_name)

    lock_changes: list[str] = []
    local_head = None
    local_branch = None
    local_dirty = False
    if repo.is_main:
        local_branch, local_head, local_dirty, lock_changes = local_git_snapshot(repo_root, since)

    return RepoSnapshot(
        name=repo.name,
        full_name=repo.full_name,
        url=str(repo_info.get("html_url") or repo.url),
        manifest_version=repo.version,
        is_main=repo.is_main,
        default_branch=default_branch,
        default_branch_sha=default_branch_sha,
        default_branch_status=default_branch_status,
        latest_tag=latest_tag,
        latest_release=latest_release,
        open_prs=open_prs,
        merged_prs=merged_prs,
        lock_changes=lock_changes,
        local_head=local_head,
        local_branch=local_branch,
        local_dirty=local_dirty,
    )


def build_questions(repos: list[RepoSnapshot], priority_queue: list[PRSnapshot]) -> list[str]:
    questions: list[str] = []
    if any(repo.default_branch_status != "success" for repo in repos):
        questions.append("是否需要优先处理默认分支状态异常的仓库？")
    if any(pr.risk == "P0" for pr in priority_queue):
        questions.append("是否先处理所有 P0 PR 再推进下一轮合并？")
    if any(repo.lock_changes for repo in repos if repo.name == "navigation_3d"):
        questions.append("是否需要针对本周的 private.repos / release 变更做一次版本冻结复盘？")
    if not questions:
        questions.append("本周无明显阻塞项，是否继续按当前节奏推进？")
    return questions


def build_heuristic_summary(data: WeeklyReviewData) -> str:
    top_priority = data.priority_queue[:8]
    lines = [
        "本周总体保持可控，但仍应优先处理高风险 PR 与默认分支状态异常的仓库。",
        "",
        f"- 扫描仓库数：{data.repo_count}",
        f"- Open PR 总数：{data.open_pr_count}",
        f"- 本周合并 PR：{data.merged_pr_count}",
        f"- P0 / P1 / P2 / P3：{data.p0_count} / {data.p1_count} / {data.p2_count} / {data.p3_count}",
        "",
        "优先处理建议：",
    ]
    if top_priority:
        for pr in top_priority:
            lines.append(
                f"- {pr.risk} {pr.repo}#{pr.number} {pr.title} "
                f"({pr.ci_state}, {pr.changed_files} files)"
            )
    else:
        lines.append("- 当前没有需要优先处理的 open PR。")
    return "\n".join(lines).strip()


def get_openai_report(
    data: WeeklyReviewData,
    model: str,
    base_url: str,
    api_key: str,
) -> str:
    payload = {
        "generated_at": data.generated_at,
        "period_start": data.period_start,
        "period_end": data.period_end,
        "repo_count": data.repo_count,
        "open_pr_count": data.open_pr_count,
        "merged_pr_count": data.merged_pr_count,
        "risk_counts": {
            "P0": data.p0_count,
            "P1": data.p1_count,
            "P2": data.p2_count,
            "P3": data.p3_count,
        },
        "repositories": [asdict(repo) for repo in data.repositories],
        "priority_queue": [asdict(pr) for pr in data.priority_queue[:12]],
        "questions": data.questions,
    }
    system_prompt = (
        "你是 navigation_3d 的周度 AI review agent。"
        "请只输出 Markdown，不要添加代码块外的解释。"
        "必须保留以下标题："
        "## 本周总览、## 主仓状态、## 子仓状态、## open PR review 清单、"
        "## 高风险项、## 建议优先处理项、## 需要人工确认的问题、## 附录。"
        "请基于输入事实做分析，不要虚构未提供的数据。"
        "请用中文，语气简洁，适合直接作为邮件正文。"
    )
    user_prompt = json.dumps(payload, ensure_ascii=False, indent=2)
    request_body = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.2,
    }
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/chat/completions",
        data=json.dumps(request_body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "navigation_3d-weekly-review",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        response_body = json.loads(response.read().decode("utf-8"))
    choices = response_body.get("choices") or []
    if not choices:
        raise RuntimeError("OpenAI response did not contain any choices")
    message = choices[0].get("message") or {}
    content = str(message.get("content") or "").strip()
    if not content:
        raise RuntimeError("OpenAI response content was empty")
    return content


def render_markdown(data: WeeklyReviewData) -> str:
    lines = [
        f"# {data.title}",
        "",
        f"- 生成时间：{data.generated_at}",
        f"- 周期范围：{data.period_start} → {data.period_end}",
        f"- 时区：{data.timezone}",
        f"- 扫描仓库：{data.repo_count}",
        f"- AI backend：{data.ai_backend}",
        "",
        "## 本周总览",
        "",
        data.ai_summary,
        "",
        "## 主仓状态",
        "",
    ]

    main_repo = next((repo for repo in data.repositories if repo.name == "navigation_3d"), None)
    if main_repo:
        lines.extend(render_repo_section(main_repo, include_prs=True, include_lock=True))
    else:
        lines.extend(["未找到主仓信息。", ""])

    lines.append("## 子仓状态")
    lines.append("")
    for repo in data.repositories:
        if repo.name == "navigation_3d":
            continue
        lines.extend(render_repo_section(repo, include_prs=False, include_lock=False))

    lines.extend(
        [
            "## open PR review 清单",
            "",
            render_pr_table(data.priority_queue),
            "",
            "## 高风险项",
            "",
            render_risk_list([pr for pr in data.priority_queue if pr.risk in {"P0", "P1"}]),
            "",
            "## 建议优先处理项",
            "",
            render_priority_list(data.priority_queue[:8]),
            "",
            "## 需要人工确认的问题",
            "",
            render_question_list(data.questions),
            "",
            "## 附录",
            "",
            render_appendix(data.repositories),
            "",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def render_repo_section(
    repo: RepoSnapshot,
    include_prs: bool,
    include_lock: bool,
) -> list[str]:
    lines = [
        f"### {repo.name}",
        "",
        f"- 仓库：`{repo.full_name}`",
        f"- 版本锁定：`{repo.manifest_version}`",
        f"- 默认分支：`{repo.default_branch}`",
        f"- 默认分支状态：`{repo.default_branch_status}`",
        f"- 最新 tag：`{repo.latest_tag or 'N/A'}`",
        f"- 最新 release：`{repo.latest_release or 'N/A'}`",
        f"- Open PR：{len(repo.open_prs)}",
        f"- 本周 merged PR：{len(repo.merged_prs)}",
    ]
    if repo.is_main:
        lines.append(f"- 本地分支：`{repo.local_branch or 'N/A'}`")
        lines.append(f"- 本地 HEAD：`{repo.local_head or 'N/A'}`")
        lines.append(f"- 本地工作区脏状态：`{'yes' if repo.local_dirty else 'no'}`")
    if include_lock and repo.lock_changes:
        lines.append("- 本周 version lock 变更：")
        for change in repo.lock_changes:
            lines.append(f"  - {change}")
    if include_prs and repo.open_prs:
        lines.append("- Open PR 明细：")
        for pr in repo.open_prs[:10]:
            lines.append(
                f"  - `{pr.risk}` {pr.repo}#{pr.number} {pr.title} "
                f"[{pr.ci_state}] ({pr.changed_files} files)"
            )
    lines.append("")
    return lines


def render_pr_table(prs: list[PRSnapshot]) -> str:
    if not prs:
        return "当前没有需要 review 的 open PR。"
    rows = [
        "| Priority | Repo | PR | CI | Files | Title |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for pr in prs:
        rows.append(
            f"| {pr.risk} | {pr.repo} | [{pr.number}]({pr.url}) | {pr.ci_state} | "
            f"{pr.changed_files} | {pr.title} |"
        )
    return "\n".join(rows)


def render_risk_list(prs: list[PRSnapshot]) -> str:
    if not prs:
        return "当前没有 P0 / P1 风险项。"
    lines = []
    for pr in prs:
        reason = "；".join(pr.risk_reasons)
        lines.append(f"- `{pr.risk}` {pr.repo}#{pr.number} {pr.title}：{reason}")
    return "\n".join(lines)


def render_priority_list(prs: list[PRSnapshot]) -> str:
    if not prs:
        return "当前没有待优先处理项。"
    lines = []
    for pr in prs:
        lines.append(
            f"- `{pr.risk}` {pr.repo}#{pr.number} {pr.title} "
            f"（CI: {pr.ci_state}，Files: {pr.changed_files}）"
        )
    return "\n".join(lines)


def render_question_list(questions: list[str]) -> str:
    return "\n".join(f"- {question}" for question in questions) if questions else "无。"


def render_appendix(repos: list[RepoSnapshot]) -> str:
    lines = [
        "### 版本与发布附录",
        "",
    ]
    for repo in repos:
        if repo.name != "navigation_3d":
            continue
        if repo.lock_changes:
            lines.append("#### 主仓 lock 变更")
            for change in repo.lock_changes:
                lines.append(f"- {change}")
        else:
            lines.append("#### 主仓 lock 变更")
            lines.append("- 本周没有检测到 `repos/private.repos` 相关提交。")
        lines.append("")
        break
    return "\n".join(lines).rstrip()


def load_github_token() -> str:
    token = current_git_token()
    if not token:
        raise RuntimeError(
            "No GitHub token found. Set WEEKLY_REVIEW_GITHUB_TOKEN, GH_TOKEN, or GITHUB_TOKEN."
        )
    return token


def build_weekly_review(
    repo_root: Path,
    manifest_path: Path,
    lookback_days: int,
    timezone_name: str,
    title: str,
    ai_backend: str,
    ai_model: str,
    ai_base_url: str,
) -> WeeklyReviewData:
    tz = ensure_timezone(timezone_name)
    now = dt.datetime.now(tz)
    start = now - dt.timedelta(days=lookback_days)
    client = GitHubClient(load_github_token())
    repo_specs = [detect_main_repo(repo_root), *parse_private_repos(manifest_path)]

    repositories = [
        repository_health(client, repo, start, repo_root) for repo in repo_specs
    ]
    priority_queue = sorted(
        [pr for repo in repositories for pr in repo.open_prs],
        key=lambda pr: (0 if pr.risk == "P0" else 1 if pr.risk == "P1" else 2 if pr.risk == "P2" else 3, -pr.risk_score, pr.updated_at),
    )
    open_pr_count = sum(len(repo.open_prs) for repo in repositories)
    merged_pr_count = sum(len(repo.merged_prs) for repo in repositories)
    counts = {
        "P0": sum(1 for pr in priority_queue if pr.risk == "P0"),
        "P1": sum(1 for pr in priority_queue if pr.risk == "P1"),
        "P2": sum(1 for pr in priority_queue if pr.risk == "P2"),
        "P3": sum(1 for pr in priority_queue if pr.risk == "P3"),
    }
    generated_at = now.strftime("%Y-%m-%d %H:%M:%S %Z")
    period_start = start.strftime("%Y-%m-%d %H:%M:%S %Z")
    period_end = now.strftime("%Y-%m-%d %H:%M:%S %Z")
    iso_week = now.isocalendar()
    report_title = title or f"navigation_3d Weekly Review | {iso_week.year}-W{iso_week.week:02d}"

    data = WeeklyReviewData(
        generated_at=generated_at,
        period_start=period_start,
        period_end=period_end,
        timezone=timezone_name,
        title=report_title,
        ai_backend=ai_backend,
        repo_count=len(repositories),
        open_pr_count=open_pr_count,
        merged_pr_count=merged_pr_count,
        p0_count=counts["P0"],
        p1_count=counts["P1"],
        p2_count=counts["P2"],
        p3_count=counts["P3"],
        repositories=repositories,
        priority_queue=priority_queue,
        questions=[],
        ai_summary="",
    )
    data.questions = build_questions(repositories, priority_queue)
    data.ai_summary = generate_ai_summary(
        data,
        ai_backend=ai_backend,
        ai_model=ai_model,
        ai_base_url=ai_base_url,
    )
    return data


def generate_ai_summary(
    data: WeeklyReviewData,
    ai_backend: str,
    ai_model: str,
    ai_base_url: str,
) -> str:
    api_key = os.environ.get("WEEKLY_REVIEW_OPENAI_API_KEY", "").strip()
    backend = ai_backend.lower().strip()
    if backend not in {"auto", "heuristic", "openai"}:
        backend = "auto"

    if backend == "heuristic" or not api_key:
        return build_heuristic_summary(data)

    if backend in {"auto", "openai"}:
        try:
            return get_openai_report(
                data,
                model=ai_model or DEFAULT_AI_MODEL,
                base_url=ai_base_url or "https://api.openai.com/v1",
                api_key=api_key,
            )
        except Exception as exc:  # pragma: no cover - fallback path
            fallback = build_heuristic_summary(data)
            return (
                f"AI agent review 生成失败，已回退到启发式摘要：{exc}\n\n"
                f"{fallback}"
            )

    return build_heuristic_summary(data)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a weekly AI-assisted review digest for navigation_3d."
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root used for local main-repo inspection.",
    )
    parser.add_argument(
        "--manifest",
        default="repos/private.repos",
        help="Path to the vcstool manifest used to enumerate child repositories.",
    )
    parser.add_argument(
        "--lookback-days",
        type=int,
        default=7,
        help="Lookback window for weekly aggregation.",
    )
    parser.add_argument(
        "--timezone",
        default=DEFAULT_TIMEZONE,
        help="Timezone used for human-readable timestamps.",
    )
    parser.add_argument(
        "--title",
        default="",
        help="Override report title.",
    )
    parser.add_argument(
        "--ai-backend",
        default="auto",
        choices=["auto", "heuristic", "openai"],
        help="AI backend to use for the weekly review.",
    )
    parser.add_argument(
        "--ai-model",
        default=DEFAULT_AI_MODEL,
        help="Model name for the OpenAI-compatible backend.",
    )
    parser.add_argument(
        "--ai-base-url",
        default="https://api.openai.com/v1",
        help="OpenAI-compatible API base URL.",
    )
    parser.add_argument(
        "--output",
        default="weekly-review.md",
        help="Markdown output path. Use '-' to print to stdout.",
    )
    parser.add_argument(
        "--json-output",
        default="",
        help="Optional JSON snapshot output path.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    manifest_path = Path(args.manifest)
    if not manifest_path.is_absolute():
        manifest_path = repo_root / manifest_path
    data = build_weekly_review(
        repo_root=repo_root,
        manifest_path=manifest_path,
        lookback_days=args.lookback_days,
        timezone_name=args.timezone,
        title=args.title,
        ai_backend=args.ai_backend,
        ai_model=args.ai_model,
        ai_base_url=args.ai_base_url,
    )
    markdown = render_markdown(data)

    if args.output == "-":
        sys.stdout.write(markdown)
    else:
        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = repo_root / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")

    if args.json_output:
        json_path = Path(args.json_output)
        if not json_path.is_absolute():
            json_path = repo_root / json_path
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(
            json.dumps(asdict(data), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

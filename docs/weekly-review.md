# Weekly Review

## Purpose

`navigation_3d` uses a weekly AI-assisted review workflow to collect repository facts,
rank open pull requests, and send a Markdown report by email.

The first version is intentionally human-in-the-loop:

- scheduled on Fridays
- manually triggerable
- read-only against GitHub data
- no automatic approve / merge / review comments

## Scope

The weekly report covers:

- the main repository `navigation_3d`
- all child repositories listed in `repos/private.repos`

The review scope includes open pull requests only. Closed PRs are only used as weekly
context for merged-change counts.

## Outputs

The workflow generates:

- `weekly-review.md`
- `weekly-review.json`

The Markdown report is the primary artifact and is also sent as an email message.

## Local Preview

Generate a report locally:

```bash
python3 scripts/weekly_review.py \
  --repo-root . \
  --manifest repos/private.repos \
  --lookback-days 7 \
  --ai-backend heuristic \
  --output weekly-review.md \
  --json-output weekly-review.json
```

If `WEEKLY_REVIEW_OPENAI_API_KEY` is configured and `--ai-backend auto` is used, the
reporter will call an OpenAI-compatible chat completion endpoint. Otherwise it falls
back to a deterministic heuristic summary.

## Email Delivery

The Markdown report is delivered through SMTP.

Required settings:

- `WEEKLY_REVIEW_FROM`
- `WEEKLY_REVIEW_TO`
- `WEEKLY_REVIEW_SMTP_HOST`

Optional settings:

- `WEEKLY_REVIEW_SMTP_PORT`
- `WEEKLY_REVIEW_SMTP_USERNAME`
- `WEEKLY_REVIEW_SMTP_PASSWORD`

The email body keeps the Markdown content so it can be copied into meeting notes or a
follow-up document without reformatting.

## GitHub Access

The weekly review collector needs a GitHub token that can read pull requests and release
metadata across the main repository and all child repositories.

Recommended setting:

- `WEEKLY_REVIEW_GITHUB_TOKEN`

Local preview can also fall back to `gh auth token` when GitHub CLI authentication is
available.

## Workflow Trigger

The GitHub Actions workflow runs in two modes:

- scheduled every Friday morning UTC
- manual `workflow_dispatch` trigger

The report uses the current `develop` state as the weekly view.

## Future Extensions

Possible future stages include:

- auto-generated review comment drafts
- repository health scoring over multiple weeks
- issue follow-up suggestions
- release readiness summaries

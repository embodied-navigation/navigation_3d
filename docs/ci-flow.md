# CI Flow

## Purpose

This repository uses a two-level CI model:

- child repositories run fast, repository-local validation
- `navigation_3d` runs workspace assembly and system integration smoke tests

The goal is to keep module-level feedback fast while still validating the composed
navigation workspace in the integration repository.

## Child Repository CI

Each active child repository should keep a lightweight CI surface:

- branch-name validation
- commit message / PR title validation
- code formatting checks
- repository-local build
- repository-local tests

Child CI should not be responsible for:

- assembling the full workspace
- importing all child repositories
- running the main integration smoke test
- launching RViz-based end-to-end validation

## Main Repository CI

`navigation_3d` owns the integration-side CI:

- `vcs import src < repos/private.repos`
- Docker image build / startup validation
- workspace build
- CTest execution
- minimal navigation smoke test
- optional RViz launch validation when secrets and environment allow it

## Shared Scripts

The current repository provides reusable scripts for both repository-local and integration
validation:

- `scripts/ci_local.sh`
- `scripts/ci_integration.sh`
- `scripts/test_navigation_smoke.sh`
- `scripts/check_branch_name.sh`
- `scripts/check_commit_msg.sh`
- `scripts/check_pr_title.sh`
- `scripts/format_check.sh`

## Integration Credentials

The integration smoke test needs access to the private child repositories referenced by
`repos/private.repos`.

Current CI expectation:

- provide a GitHub Actions secret named `NAVIGATION_3D_CI_SSH_KEY`
- configure `webfactory/ssh-agent` in the main repository workflow
- allow the integration job to fetch private child repositories over SSH
- mount the repository `config/` directory into the container so the Fast DDS profile under
  `/root/config/fastdds_shm.xml` is available during smoke execution

When the secret is not configured, the integration smoke job is skipped and the workflow
still completes its repository-local checks.

## Merge Gate

Recommended final completion rule:

1. child repository PR passes its own CI
2. the main repository updates `repos/private.repos`
3. the main repository integration smoke test passes
4. the main repository PR merges

This keeps module-level changes fast while ensuring the composed workspace remains
reproducible.

The integration smoke is intentionally lighter than the manual end-to-end navigation test:
it only requires a goal publication, a plan publication, and a controller status update,
while the full `scripts/test_minimal_navigation.sh` loop remains available for deeper
validation.

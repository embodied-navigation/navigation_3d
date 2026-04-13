# Release Notes

## Purpose

`navigation_3d` generates changelog drafts and release notes from Conventional Commits,
merged PR titles, and Git tags.

The current policy is:

- development changes accumulate into a draft changelog
- stable version descriptions are frozen on release tags
- Git tags are the source of truth for release versions

## Local Draft Generation

Generate a draft from the latest tag to `HEAD`:

```bash
./scripts/release_notes.py --draft --output /tmp/release-notes.md
```

Generate a draft for an explicit range:

```bash
./scripts/release_notes.py --from v0.1.0 --to HEAD --title Unreleased
```

The output is grouped by commit type:

- `feat`
- `fix`
- `docs`
- `refactor`
- `test`
- `chore`
- `style`
- `breaking`

## Tag-Based Release Notes

When a release tag is pushed, the repository automatically generates a GitHub Release body
from the tag range and publishes it through:

- [`/.github/workflows/release-notes.yml`](../.github/workflows/release-notes.yml)

This workflow uses the same generator script as the local draft flow:

- [`scripts/release_notes.py`](../scripts/release_notes.py)

## Archiving

If the team wants to keep a repository-local archive, the generated Markdown can be saved
under:

- `docs/releases/<tag>.md`

That archive is optional and can be updated manually from the generated output when a
release is frozen.

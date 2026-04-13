# Release Archive

This directory is reserved for frozen release note snapshots such as:

- `docs/releases/v0.1.0.md`
- `docs/releases/v0.1.1.md`

Generate release text with:

```bash
./scripts/release_notes.py --draft
```

or for a frozen tag:

```bash
./scripts/release_notes.py --from v0.1.0 --to v0.1.1 --title v0.1.1
```

The repository's official version source remains Git tags. These archived files are
human-readable snapshots only.

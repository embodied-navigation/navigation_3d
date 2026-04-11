# Objective

Enforce the documented branch naming policy locally through `pre-commit`.

# Constraints

- Reuse the existing `scripts/check_branch_name.sh`.
- Keep the change small and aligned with the current Git workflow.
- Avoid changing unrelated developer tooling.

# Next Steps

- Add a local `pre-commit` hook for branch name validation.
- Update contributor guidance to mention the local enforcement.
- Run the smallest useful validation for the hook configuration.

# Open Questions

- None for this incremental workflow update.

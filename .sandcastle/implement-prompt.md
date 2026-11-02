# TASK

Issue {{TASK_ID}}: {{ISSUE_TITLE}}. Branch {{BRANCH}}.

Read it with `gh issue view {{TASK_ID}}`. Work on this issue only.

Recent commits:

!`git log -n 5 --format="%h %ad %s" --date=short`

# METHOD

Read only the files the issue names and the tests next to them. Do not scan the repo. CLAUDE.md has the project rules.

Work test first. Write one failing test, make it pass, repeat. Then tidy.

# CHECKS

Run these before each commit:

1. `make format-check lint typecheck`
2. `python -m pytest -q -x` on the test files for the area you changed

The full suite is slow, so leave it to `make check`, which the merge step runs once. If you change benchmark output, also run `make benchmark-golden-check` and `make provenance-check`.

# COMMIT

One commit per working step. Use a conventional subject, such as `feat(eval): ...` or `fix(fdir): ...`. In the body, write what changed and why, in a few short lines.

# STOP

If the issue is not done, comment on it with what was done. Do not close it.

When done, output <promise>COMPLETE</promise>.

Single task only.
